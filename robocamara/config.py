"""All configuration for RoboCamara lives here.

Edit this file to change pins, timings, the hotspot name, etc.
"""
from pathlib import Path

# --- Paths -----------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
PHOTOS_DIR = BASE_DIR / "photos"          # downloaded copies served to phones

# --- GPIO ------------------------------------------------------------------
# Push button (wired between this pin and GND) that dismisses the photo and
# returns the screen to the live feed. It does NOT take photos.
RESET_BUTTON_PIN = 4
BUTTON_BOUNCE_TIME = 0.1                   # seconds, debounce

# --- Camera ----------------------------------------------------------------
# Keep the original full-resolution file on the camera's SD card (a backup)
# and download a copy to the Pi. "Memory card" also makes the FILE_ADDED
# event return instantly instead of blocking the live feed for ~1s.
CAPTURE_TARGET_MATCH = "card"             # matched against the camera's choices
PHOTO_EXTENSIONS = (".jpg", ".jpeg")      # ignore RAW (.cr3/.cr2) captures
EVENT_TIMEOUT_MS = 10                     # how long to wait for camera events
MAX_PREVIEW_ERRORS = 15                   # consecutive errors before reconnect

# --- Display ---------------------------------------------------------------
SDL_VIDEODRIVER = "kmsdrm"                # render straight to HDMI, no desktop
BACKGROUND_COLOR = (0, 0, 0)
HINT_TEXT = "Scan to get your photo"

# --- Network / captive portal ---------------------------------------------
WIFI_SSID = "RoboCamara"                  # open hotspot guests join
WIFI_PASSWORD = ""                        # leave empty for an OPEN network
AP_IP = "10.42.0.1"                       # NetworkManager 'shared' gateway IP
WEB_PORT = 8080                           # port 80 is redirected here

# --- Photo lifetime --------------------------------------------------------
PHOTO_TTL_SECONDS = 10 * 60               # auto-delete 10 minutes after capture
CLEANUP_INTERVAL_SECONDS = 5

# --- Branding (shown on the phone page) ------------------------------------
SITE_TITLE = "RoboCamara"
