"""The Wi-Fi QR code drawn in the corner of every captured photo.

Scanning it joins the open hotspot; the captive portal then opens the photo
automatically. The payload is the standard Wi-Fi-join string, so iOS and
Android both recognise it from the Camera app.
"""
import qrcode
import pygame

from . import config


def _wifi_payload(ssid: str, password: str) -> str:
    if password:
        return f"WIFI:T:WPA;S:{ssid};P:{password};;"
    return f"WIFI:T:nopass;S:{ssid};;"


def make_qr_surface(box_px: int) -> pygame.Surface:
    """Return a square ``box_px``-wide pygame surface: the Wi-Fi QR on a white
    card so it scans reliably no matter what is behind it."""
    qr = qrcode.QRCode(
        border=3,
        box_size=10,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
    )
    qr.add_data(_wifi_payload(config.WIFI_SSID, config.WIFI_PASSWORD))
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    image = image.resize((box_px, box_px))
    return pygame.image.fromstring(image.tobytes(), image.size, image.mode)
