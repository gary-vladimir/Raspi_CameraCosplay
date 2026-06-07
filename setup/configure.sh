#!/usr/bin/env bash
#
# RoboCamara — STEP 2: network + auto-start.
#
# Run this AFTER install.sh, AFTER you've confirmed the camera works, and
# IDEALLY from the Pi's own keyboard/console or over Ethernet — because this
# turns wlan0 into a hotspot, so any SSH session over Wi-Fi will drop.
#
#     bash setup/configure.sh
#
# It is safe to run once. Reboot when it finishes.
#
set -euo pipefail
cd "$(dirname "$0")/.."

REPO="$(pwd)"
USER_NAME="$(whoami)"
SSID="RoboCamara"          # keep in sync with robocamara/config.py
AP_IP="10.42.0.1"
WEB_PORT="8080"

echo "============================================================"
echo " This will turn Wi-Fi (wlan0) into the open hotspot '$SSID'."
echo " The Pi will no longer use Wi-Fi for internet afterwards."
echo "============================================================"

# --- Open Wi-Fi hotspot via NetworkManager --------------------------------
echo "==> Creating the open hotspot '$SSID'"
sudo nmcli connection delete robocamara-ap >/dev/null 2>&1 || true
sudo nmcli connection add type wifi ifname wlan0 con-name robocamara-ap \
  autoconnect yes ssid "$SSID"
sudo nmcli connection modify robocamara-ap \
  802-11-wireless.mode ap \
  802-11-wireless.band bg \
  ipv4.method shared \
  ipv4.addresses "${AP_IP}/24"
# Open network (no password). If your Pi refuses to start an open AP, see the
# README "Hotspot won't start" note (you can add a password and the QR will
# still auto-join, no typing required).

# --- Captive portal DNS: resolve every domain to the Pi -------------------
echo "==> Captive DNS (every domain -> the Pi)"
sudo mkdir -p /etc/NetworkManager/dnsmasq-shared.d
echo "address=/#/${AP_IP}" | \
  sudo tee /etc/NetworkManager/dnsmasq-shared.d/captive.conf >/dev/null

# --- Firewall -------------------------------------------------------------
echo "==> Firewall: web only on Wi-Fi; SSH and everything else blocked there"
add_nat() { sudo iptables -t nat -C "$@" 2>/dev/null || sudo iptables -t nat -A "$@"; }
add_in()  { sudo iptables       -C INPUT "$@" 2>/dev/null || sudo iptables       -A INPUT "$@"; }

# redirect plain http on the hotspot to our server
add_nat PREROUTING -i wlan0 -p tcp --dport 80 -j REDIRECT --to-ports "${WEB_PORT}"
# allow only what the booth needs from Wi-Fi clients
add_in -i lo -j ACCEPT
add_in -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
add_in -i wlan0 -p udp --dport 67 -j ACCEPT      # DHCP
add_in -i wlan0 -p udp --dport 53 -j ACCEPT      # DNS
add_in -i wlan0 -p tcp --dport 53 -j ACCEPT      # DNS
add_in -i wlan0 -p tcp --dport "${WEB_PORT}" -j ACCEPT
add_in -i wlan0 -p icmp -j ACCEPT
add_in -i wlan0 -j DROP                           # block SSH etc. over Wi-Fi
sudo netfilter-persistent save

# --- systemd service ------------------------------------------------------
echo "==> Installing the auto-start service"
sudo tee /etc/systemd/system/robocamara.service >/dev/null <<EOF
[Unit]
Description=RoboCamara photo booth
After=multi-user.target
Conflicts=getty@tty1.service

[Service]
Type=simple
User=${USER_NAME}
SupplementaryGroups=video render input gpio
WorkingDirectory=${REPO}
Environment=SDL_VIDEODRIVER=kmsdrm
Environment=SDL_AUDIODRIVER=dummy
ExecStart=${REPO}/.venv/bin/python -m robocamara
Restart=always
RestartSec=5
TTYPath=/dev/tty1
StandardInput=tty
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "==> Freeing tty1 for the kiosk screen"
sudo systemctl disable getty@tty1.service >/dev/null 2>&1 || true

sudo systemctl daemon-reload
sudo systemctl enable robocamara.service

cat <<EOF

------------------------------------------------------------------
Configuration complete. Reboot to start the booth:

     sudo reboot

After it boots: the monitor shows the live feed, and phones will
see the open Wi-Fi network '${SSID}'.
------------------------------------------------------------------
EOF
