#!/usr/bin/env bash
#
# RoboCamara — STEP 1: install dependencies.
#
# Run this FIRST, while the Pi still has internet (Ethernet or your home
# Wi-Fi). Run it as the normal user (e.g. 'pi'), NOT with sudo:
#
#     bash setup/install.sh
#
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Installing system packages"
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update
sudo apt-get install -y \
  python3-venv python3-dev \
  libdrm2 libgbm1 \
  libsdl2-2.0-0 libsdl2-image-2.0-0 libsdl2-ttf-2.0-0 \
  libusb-1.0-0 \
  network-manager dnsmasq-base iptables-persistent

echo "==> Creating the Python virtual environment (.venv)"
python3 -m venv .venv
./.venv/bin/pip install --upgrade pip wheel
./.venv/bin/pip install pygame Pillow qrcode Flask waitress gpiozero lgpio

echo "==> Installing python-gphoto2 from PyPI (bundles libgphoto2 >= 2.5.34)"
# The Canon T8i / EOS 850D USB id needs libgphoto2 >= 2.5.31, which the
# Raspberry Pi OS / piwheels build may not provide. Forcing the PyPI wheel
# guarantees a recent bundled libgphoto2.
./.venv/bin/pip install --upgrade --force-reinstall --no-deps \
  --index-url https://pypi.org/simple --only-binary :all: gphoto2

echo "==> Adding '$USER' to the hardware groups (video render input gpio)"
sudo usermod -aG video,render,input,gpio "$USER"

cat <<'EOF'

------------------------------------------------------------------
Install complete.

1) Plug in the camera, turn it ON, then test that the Pi sees it:

     ./.venv/bin/python - <<'PY'
     import gphoto2 as gp
     c = gp.Camera(); c.init()
     print("Camera OK:", c.get_summary().text.splitlines()[0])
     c.exit()
     PY

2) Reboot once so the new group membership takes effect:

     sudo reboot

3) Then run STEP 2:   bash setup/configure.sh
------------------------------------------------------------------
EOF
