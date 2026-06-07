"""Canon control over USB via libgphoto2 (the python-gphoto2 binding).

A USB camera allows only one session, so a single connection both streams
the live feed and reports photos taken with the camera's own shutter button.
Each loop iteration we:

    1. drain camera events  -> a physical shutter press shows up as
       GP_EVENT_FILE_ADDED, which we download;
    2. grab one preview frame for the live feed.

This is the pattern the libgphoto2 maintainers recommend for Canon EOS.
"""
import subprocess
import time

import gphoto2 as gp

from . import config

# Desktop helpers that auto-claim the camera and must be cleared first.
# (On Raspberry Pi OS Lite these usually aren't running — the pkill is a
# harmless safety net.)
_GRABBERS = ("gvfsd-gphoto2", "gvfs-gphoto2-volume-monitor")


class Camera:
    """A live, connected Canon camera."""

    def __init__(self):
        self._release_grabbers()
        self._camera = gp.Camera()
        self._camera.init()                      # raises gp.GPhoto2Error if absent
        self._configure()

    # -- setup --------------------------------------------------------------
    @staticmethod
    def _release_grabbers():
        for name in _GRABBERS:
            subprocess.run(["pkill", "-f", name],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _set_value(self, name, value):
        """Set a simple (toggle/text) config value, ignoring missing keys."""
        try:
            cfg = self._camera.get_single_config(name)
            cfg.set_value(value)
            self._camera.set_single_config(name, cfg)
        except gp.GPhoto2Error:
            pass

    def _set_choice(self, name, match):
        """Set a radio config to the first choice containing ``match``."""
        try:
            cfg = self._camera.get_single_config(name)
            choices = list(cfg.get_choices())
        except gp.GPhoto2Error:
            return
        target = next((c for c in choices if match.lower() in c.lower()), None)
        if target is not None:
            try:
                cfg.set_value(target)
                self._camera.set_single_config(name, cfg)
            except gp.GPhoto2Error:
                pass

    def _configure(self):
        # Keep the original on the SD card and make the capture event instant.
        self._set_choice("capturetarget", config.CAPTURE_TARGET_MATCH)
        # Start live view explicitly (capture_preview also does this).
        self._set_value("eosviewfinder", 1)
        self._set_value("viewfinder", 1)
        # Don't let the camera fall asleep mid-event.
        self._set_value("autopoweroff", "0")

    # -- live feed ----------------------------------------------------------
    def live_frame(self) -> bytes:
        """Return one JPEG live-view frame (and keep live view alive)."""
        camera_file = self._camera.capture_preview()
        return bytes(camera_file.get_data_and_size())

    # -- capture detection --------------------------------------------------
    def poll_capture(self, timeout_ms=config.EVENT_TIMEOUT_MS):
        """Return a CameraFilePath if a photo was just taken, else None.

        RAW files are skipped so only the displayable JPEG triggers a capture.
        """
        event_type, event_data = self._camera.wait_for_event(timeout_ms)
        if event_type == gp.GP_EVENT_FILE_ADDED:
            if event_data.name.lower().endswith(config.PHOTO_EXTENSIONS):
                return event_data
        return None

    def download(self, path, dest):
        """Download a captured file (CameraFilePath) from the camera to disk."""
        camera_file = self._camera.file_get(
            path.folder, path.name, gp.GP_FILE_TYPE_NORMAL)
        camera_file.save(str(dest))

    # -- teardown -----------------------------------------------------------
    def close(self):
        try:
            self._camera.exit()
        except gp.GPhoto2Error:
            pass


def connect(display=None):
    """Block until a camera is reachable, showing progress on the monitor."""
    while True:
        try:
            return Camera()
        except gp.GPhoto2Error:
            if display is not None:
                display.show_message("Turn the camera on / check the USB cable…")
                display.pump()
            time.sleep(1.0)
