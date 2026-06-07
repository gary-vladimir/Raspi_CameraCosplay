"""RoboCamara — a wearable Canon photo booth for the Raspberry Pi.

The package is split into small, single-purpose modules:

    config   — all tunables in one place
    camera   — Canon control over USB (live view + shutter detection)
    display  — full-screen HDMI output (live feed and captured photo)
    overlay  — the Wi-Fi QR code drawn on the photo
    store    — captured photos with a 10-minute time-to-live
    server   — mobile web app + captive portal
    app      — the orchestrator that ties it all together

Run it with:  python -m robocamara
"""

__version__ = "1.0.0"
