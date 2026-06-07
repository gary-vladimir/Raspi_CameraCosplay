"""Full-screen HDMI output, rendered straight to the framebuffer (KMSDRM).

One pygame window shows two things depending on state:
  * the live feed (a stream of JPEG frames from the camera), and
  * a captured photo with the Wi-Fi QR code in the bottom-right corner.
"""
import io
import os

import pygame

from . import config, overlay


class Display:
    def __init__(self):
        os.environ.setdefault("SDL_VIDEODRIVER", config.SDL_VIDEODRIVER)
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")   # no audio on a kiosk
        pygame.display.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
        self.width, self.height = self.screen.get_size()

        qr_size = int(self.height * 0.22)
        self.qr = overlay.make_qr_surface(qr_size)
        self.margin = int(self.height * 0.03)
        self.font = pygame.font.Font(None, int(self.height * 0.05))

    # -- internal -----------------------------------------------------------
    def _blit_fit(self, surface, smooth=False):
        """Scale ``surface`` to fill the screen (letterboxed) and draw it."""
        sw, sh = surface.get_size()
        scale = min(self.width / sw, self.height / sh)
        size = (max(1, int(sw * scale)), max(1, int(sh * scale)))
        scaler = pygame.transform.smoothscale if smooth else pygame.transform.scale
        scaled = scaler(surface, size)
        self.screen.fill(config.BACKGROUND_COLOR)
        self.screen.blit(scaled, ((self.width - size[0]) // 2,
                                  (self.height - size[1]) // 2))

    # -- states -------------------------------------------------------------
    def show_live(self, jpeg_bytes):
        surface = pygame.image.load(io.BytesIO(jpeg_bytes))
        self._blit_fit(surface, smooth=False)
        pygame.display.flip()

    def show_photo(self, path):
        surface = pygame.image.load(str(path))
        self._blit_fit(surface, smooth=True)

        qx = self.width - self.qr.get_width() - self.margin
        qy = self.height - self.qr.get_height() - self.margin
        hint = self.font.render(config.HINT_TEXT, True, (255, 255, 255))
        self.screen.blit(hint, (qx + (self.qr.get_width() - hint.get_width()) // 2,
                                qy - hint.get_height() - 8))
        self.screen.blit(self.qr, (qx, qy))
        pygame.display.flip()

    def show_message(self, text):
        self.screen.fill(config.BACKGROUND_COLOR)
        label = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(label, ((self.width - label.get_width()) // 2,
                                 (self.height - label.get_height()) // 2))
        pygame.display.flip()

    # -- housekeeping -------------------------------------------------------
    def pump(self):
        """Process the SDL event queue; raise to quit on window-close/ESC."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                raise KeyboardInterrupt

    def close(self):
        pygame.quit()
