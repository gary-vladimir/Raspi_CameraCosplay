# RoboCamara 📷

A wearable, giant-Canon-camera photo booth built on a Raspberry Pi.

The monitor on the back of the costume shows a **live feed** of whatever the
real Canon inside is pointing at. When you press the camera's shutter, the
photo freezes on the screen with a **QR code** in the corner. A guest scans
it with any phone, instantly joins the booth's own Wi-Fi, and a page pops open
with **their photo to download**. Ten minutes later the photo is automatically
deleted from the Pi. Press the **reset button** and the screen returns to the
live feed, ready for the next person.

No internet, no app, no Wi-Fi password, no Bluetooth.

---

## How it works

```
   Canon Rebel T8i ──USB──► Raspberry Pi 4 ──HDMI──► Monitor (live feed / photo)
                                  │
                                  ├─ open Wi-Fi hotspot "RoboCamara"
                                  └─ captive web page  ──► guest's phone (download)

   Reset push button ──GPIO──► Pi   (returns the screen to the live feed)
```

1. The Pi streams the camera's live view to the monitor (full screen).
2. You frame the shot on the monitor and press the **camera's own shutter**.
   The Pi detects the photo over USB and downloads it.
3. The photo is shown full screen with a Wi-Fi QR code bottom-right, and a
   copy is published to the Pi's tiny web server with a 10-minute timer.
4. A guest scans the QR → their phone joins the open hotspot → a page opens
   automatically showing the photo, a countdown, and a download button.
5. You press the reset button → back to the live feed.
6. After 10 minutes the Pi deletes its copy (the full-res original stays on
   the camera's SD card).

### Why the camera's shutter, not the button?

You asked whether ISO / shutter / aperture / **focus** can be driven from the
Pi. Short answer from the research (sources at the bottom): exposure can be
set over USB in Manual mode, but **focus control via gphoto2 is severely
limited** — there is no autofocus-point selection and no absolute focus
position on this camera class. To get sharp photos you need to focus on the
camera normally, so RoboCamara lets you shoot with the **real shutter** (full
focus control) and uses the GPIO button only to reset the screen.

---

## Hardware checklist

| Part | Notes |
|------|-------|
| Raspberry Pi 4 Model B | 2 GB+ is plenty |
| microSD card (for the Pi) | 16 GB+, for Raspberry Pi OS |
| Canon Rebel T8i (EOS 850D) | with **an SD card inserted** (photos save there) |
| USB cable | camera → Pi (use a Pi **USB-3**, blue, port) |
| HDMI monitor | connect to the Pi's **HDMI0** port (next to USB-C power) |
| micro-HDMI → HDMI cable | for the monitor |
| Push button | momentary, wired between **GPIO4** and **GND** |
| Power | a solid 5V/3A USB-C supply for the Pi; for the camera, a dummy battery / AC adapter is best for long events |

**Button wiring:** one leg to **GPIO4** (physical pin 7), the other leg to any
**GND** (e.g. physical pin 6 or 9). No resistor needed — the Pi's internal
pull-up is used. See `images/connections.png`.

---

## Setup — from a factory-fresh Pi

You only do Parts 1–5 once. Everything after that is automatic on boot.

### Part 1 — Flash the SD card

1. On your computer install **[Raspberry Pi Imager](https://www.raspberrypi.com/software/)**.
2. Choose OS → **Raspberry Pi OS (other)** → **Raspberry Pi OS Lite (64-bit)**.
   *(Lite = no desktop. This is intentional: it's leaner and avoids a Pi
   service that would otherwise fight us for the camera.)*
3. Choose your Pi's microSD card.
4. Click the **⚙ / Edit Settings** (OS customisation) and set:
   - **Hostname:** `robocamara`
   - **Username / password:** e.g. `pi` and a password you'll remember
   - **Wi-Fi:** your home Wi-Fi name + password *(only for setup downloads;
     we switch the Pi to its own hotspot later)*
   - **Wi-Fi country:** set this correctly (e.g. `US`, `MX`) — **required**
     or the hotspot won't start later
   - **Locale / timezone:** your own
   - **Services tab → Enable SSH** (password authentication is fine)
5. Write the card, then put it in the Pi.

### Part 2 — First boot & connect

1. Insert the SD card, connect the HDMI monitor and Ethernet (recommended) or
   rely on the home Wi-Fi you set, then power on the Pi.
2. From your computer, SSH in:
   ```bash
   ssh pi@robocamara.local
   ```
   *(If that name doesn't resolve, find the Pi's IP in your router and use
   `ssh pi@<ip>`.)*

### Part 3 — Get the code onto the Pi

Push this project to your own GitHub (from your Mac), then on the Pi:

```bash
git clone https://github.com/<you>/Raspi_CameraCosplay.git ~/Raspi_CameraCosplay
cd ~/Raspi_CameraCosplay
```

*(No GitHub? Copy the folder over with `scp -r Raspi_CameraCosplay pi@robocamara.local:~/` from your Mac instead.)*

### Part 4 — Install dependencies & test the camera

```bash
bash setup/install.sh
```

This installs the system libraries, builds a Python virtual environment, and
installs the correct `gphoto2` (the one that recognises the T8i). When it
finishes, **turn the camera on, connect the USB cable**, and test:

```bash
./.venv/bin/python - <<'PY'
import gphoto2 as gp
c = gp.Camera(); c.init()
print("Camera OK:", c.get_summary().text.splitlines()[0])
c.exit()
PY
```

You should see `Camera OK: ...`. If you see an error, check
[Troubleshooting](#troubleshooting). Then reboot once so your new permissions
take effect:

```bash
sudo reboot
```

### Part 5 — Set up the hotspot & auto-start

> ⚠️ This turns the Pi's Wi-Fi into the **RoboCamara hotspot**, so if you are
> connected over Wi-Fi your SSH session will drop. Run it from the Pi's own
> keyboard, or over **Ethernet**.

```bash
cd ~/Raspi_CameraCosplay
bash setup/configure.sh
sudo reboot
```

That's it. After this reboot the booth starts automatically every time the Pi
powers on.

---

## Set up the camera (one-time)

On the Canon itself:

- **Mode dial:** `P` (or `M` if you want full manual control).
- **Image quality:** a **JPEG** setting (e.g. Large/Fine). RoboCamara ignores
  RAW files, so RAW-only won't display. RAW+JPEG is fine (the JPEG is used).
- **SD card:** must be inserted — captured photos are written there.
- **Lens AF/MF:** your choice; you focus normally with a half-press.
- Optional: turn the camera's own auto-power-off down or use a dummy
  battery / AC adapter for long events.

---

## Using it day-to-day

1. Power on the Pi (camera on, USB connected). After ~30–40s the monitor
   shows the live feed.
2. Frame your subject on the monitor and **press the camera shutter**.
3. The photo appears full screen with the QR code. The guest:
   - opens their phone **camera** and points it at the QR,
   - taps the prompt to **join "RoboCamara"** (no password),
   - a page opens automatically with their photo + a countdown,
   - **Android:** taps **Download photo**. **iPhone:** press-and-hold the
     photo → **Save to Photos**.
4. Press the **reset button** to return to the live feed for the next person.

The full-resolution originals accumulate on the camera's SD card; the Pi only
keeps each photo for 10 minutes.

---

## Managing the service

```bash
sudo systemctl status robocamara      # is it running?
sudo journalctl -u robocamara -f      # live logs
sudo systemctl restart robocamara     # restart
sudo systemctl stop robocamara        # stop (e.g. to test by hand)
```

Run it by hand for debugging (do this on the Pi's own screen, not over SSH):

```bash
sudo systemctl stop robocamara
cd ~/Raspi_CameraCosplay
./.venv/bin/python -m robocamara
```

**Update the code later:**

```bash
cd ~/Raspi_CameraCosplay
git pull
sudo systemctl restart robocamara
```

---

## Security

This matches the priorities in `about.md`:

- **No upload endpoint exists.** Photos only ever come from the camera, so no
  one on the network can push images onto the server.
- **Unguessable links.** Each photo is served only at a random token URL;
  there is no directory listing and no way to browse other people's photos.
- **Locked-down hotspot.** The firewall (`setup/configure.sh`) allows guests
  to reach *only* the web page. **SSH and everything else are blocked over
  Wi-Fi** — you administer the Pi over Ethernet or its own keyboard.
- **Auto-deletion.** Each photo is wiped from the Pi 10 minutes after capture,
  and all photos are cleared on every reboot.

Anyone who scans a QR while a photo is on screen can see that photo — that is
expected and accepted in `about.md`.

To change the default login password: `passwd`.

---

## Customising

All knobs live in `robocamara/config.py`:

| Setting | Meaning |
|---------|---------|
| `RESET_BUTTON_PIN` | GPIO pin for the reset button (default 4) |
| `WIFI_SSID` | hotspot name (keep in sync with `setup/configure.sh`) |
| `WIFI_PASSWORD` | leave empty for an open network |
| `PHOTO_TTL_SECONDS` | how long photos live (default 600 = 10 min) |
| `HINT_TEXT` | the caption shown above the QR on the monitor |
| `SITE_TITLE` | title shown on the phone page |

After editing: `sudo systemctl restart robocamara`.

---

## Troubleshooting

**Camera not detected / "Could not claim the USB device"**
- Make sure the camera is **on** and not showing a menu; try a different USB
  cable/port. Re-run the test snippet in Part 4.
- Something else may be holding the camera: `pkill -f gvfsd-gphoto2` (harmless
  if nothing is running — RoboCamara also does this automatically).
- Confirm the gphoto2 library is new enough for the T8i:
  ```bash
  ./.venv/bin/python -c "import gphoto2 as gp; print(gp.gp_library_version(gp.GP_VERSION_SHORT))"
  ```
  It must be **≥ 2.5.31**. If not, re-run `setup/install.sh`.

**Nothing on the monitor / "kmsdrm not available"**
- Use the Pi's **HDMI0** port and reboot.
- Make sure you rebooted after `install.sh` (group membership for the screen).
- Check the logs: `sudo journalctl -u robocamara -n 50`.
- As a last resort, rebuild pygame against the system SDL:
  ```bash
  sudo apt install -y libsdl2-dev libsdl2-image-dev libsdl2-ttf-dev libfreetype6-dev
  ./.venv/bin/pip install --no-binary pygame --force-reinstall pygame
  ```

**Live feed is choppy** — this is normal. Canon USB live view is ~8–10 fps.

**Hotspot "RoboCamara" doesn't appear**
- The Wi-Fi **country** must be set: `sudo raspi-config` → Localisation →
  WLAN Country, then reboot.
- Check it: `nmcli connection show robocamara-ap` and
  `nmcli device status`.
- If your Pi refuses to start an **open** AP, give it a password (it stays
  zero-typing for guests because the QR carries it): set `WIFI_PASSWORD` in
  `config.py`, then
  ```bash
  sudo nmcli connection modify robocamara-ap wifi-sec.key-mgmt wpa-psk wifi-sec.psk "yourpass"
  sudo systemctl restart robocamara && sudo reboot
  ```

**Phone joins but no page pops up (captive portal)**
- On some phones, after joining tap the Wi-Fi network → "Sign in", or just
  open a browser to `http://10.42.0.1`.
- Confirm the captive DNS file exists:
  `cat /etc/NetworkManager/dnsmasq-shared.d/captive.conf` → `address=/#/10.42.0.1`.

**iPhone won't download** — iOS can't trigger file downloads from a web page.
Press-and-hold the photo and choose **Save to Photos** (the page shows this
hint automatically on iPhones).

---

## Camera-control research (June 2026)

Findings behind the design decisions, in case you want to revisit them:

- **Exposure (ISO / shutter / aperture)** *can* be set over USB with
  `gphoto2 --set-config iso=… shutterspeed=… aperture=…`, but shutter and
  aperture are only writable when the mode dial is on **M** (or Tv/Av for the
  matching one). Reliability is firmware-dependent.
- **Focus** is the blocker: gphoto2 offers only relative focus nudges
  (`manualfocusdrive`) and a single-shot `autofocusdrive`, with **no
  AF-point selection and no absolute focus position** on Canon EOS bodies.
  That's why we shoot with the physical shutter for full focus control.
- **Live view + physical-shutter detection** on one USB connection is the
  documented Canon pattern: interleave `capture_preview()` and
  `wait_for_event()`; a real shutter press surfaces as `GP_EVENT_FILE_ADDED`.
  Use `capturetarget=Memory card` so that event returns instantly.

Sources: gphoto.org/doc/remote · libgphoto2 issues
[#300](https://github.com/gphoto/libgphoto2/issues/300),
[#358](https://github.com/gphoto/libgphoto2/issues/358),
[#151](https://github.com/gphoto/libgphoto2/issues/151) ·
gphoto2 issues
[#471](https://github.com/gphoto/gphoto2/issues/471),
[#478](https://github.com/gphoto/gphoto2/issues/478).
