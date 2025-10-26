#!/bin/bash

# RoboCamara Auto-Start Installation Script

echo "Installing RoboCamara auto-start service..."

# Copy service file to systemd
sudo cp /home/robotgenio/robotcamara/scripts/robocamara.service /etc/systemd/system/robocamara.service

# Reload systemd
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable robocamara.service

# Start the service now
sudo systemctl start robocamara.service

echo ""
echo "Installation complete!"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status robocamara    - Check service status"
echo "  sudo systemctl stop robocamara      - Stop the service"
echo "  sudo systemctl start robocamara     - Start the service"
echo "  sudo systemctl restart robocamara   - Restart the service"
echo "  sudo systemctl disable robocamara   - Disable auto-start"
echo "  sudo journalctl -u robocamara -f    - View live logs"
echo ""
