"""The orchestrator: a two-state machine tying camera, screen and web together.

    LIVE  — stream the camera to the monitor; watch for a shutter press.
    PHOTO — show the captured photo + QR until the reset button is pressed.

The web server and the photo-cleanup timer run in background threads; the
camera and the display are driven from this main loop (libgphoto2 and SDL
both want a single owning thread).
"""
import threading
import time

import gphoto2 as gp
from gpiozero import Button

from . import camera as cameralib
from . import config, server
from .display import Display
from .store import PhotoStore

LIVE, PHOTO = "live", "photo"


class RoboCamara:
    def __init__(self):
        self.display = Display()
        self.store = PhotoStore()
        self.camera = None
        self.state = LIVE
        self._preview_errors = 0
        self._reset = threading.Event()

        self.button = Button(config.RESET_BUTTON_PIN,
                             bounce_time=config.BUTTON_BOUNCE_TIME)
        self.button.when_pressed = lambda: self._reset.set()

    # -- main loop ----------------------------------------------------------
    def run(self):
        server.serve_in_background(self.store)
        threading.Thread(target=self.store.run_cleanup_loop, daemon=True).start()

        try:
            self.display.show_message("Starting…")
            self.camera = cameralib.connect(self.display)
            while True:
                self.display.pump()
                if self.state == LIVE:
                    self._live_step()
                else:
                    self._photo_step()
        except KeyboardInterrupt:
            pass
        finally:
            self._shutdown()

    # -- states -------------------------------------------------------------
    def _live_step(self):
        # Always check for a shutter press first so we never miss a capture.
        try:
            event = self.camera.poll_capture()
        except gp.GPhoto2Error:
            event = None
        if event is not None:
            self._handle_capture(event)
            return

        # Then draw one live-view frame.
        try:
            self.display.show_live(self.camera.live_frame())
            self._preview_errors = 0
        except gp.GPhoto2Error as error:
            self._on_preview_error(error)

    def _photo_step(self):
        if self._reset.is_set():
            self._reset.clear()
            try:
                self.camera.flush_events()
            except gp.GPhoto2Error:
                pass
            self.state = LIVE
        else:
            time.sleep(0.05)

    # -- helpers ------------------------------------------------------------
    def _handle_capture(self, event):
        self.display.show_message("Got it!")
        incoming = config.PHOTOS_DIR / "_incoming.jpg"
        incoming.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.camera.download(event, incoming)
        except gp.GPhoto2Error as error:
            self._on_preview_error(error)
            return
        photo = self.store.add(incoming)
        self.display.show_photo(photo.path)
        self._reset.clear()
        self.state = PHOTO

    def _on_preview_error(self, error):
        # CAMERA_BUSY happens for a moment around a capture — just skip a frame.
        if error.code == gp.GP_ERROR_CAMERA_BUSY:
            return
        self._preview_errors += 1
        if self._preview_errors >= config.MAX_PREVIEW_ERRORS:
            self._reconnect()
        else:
            time.sleep(0.1)

    def _reconnect(self):
        self._preview_errors = 0
        if self.camera:
            self.camera.close()
        self.camera = None
        self.display.show_message("Reconnecting to camera…")
        self.camera = cameralib.connect(self.display)
        self.state = LIVE

    def _shutdown(self):
        if self.camera:
            self.camera.close()
        try:
            self.button.close()
        except Exception:
            pass
        self.display.close()


def main():
    RoboCamara().run()
