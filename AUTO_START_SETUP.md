# Auto-Start Setup for RoboCamara

This guide explains how to set up RoboCamara to automatically run on Raspberry Pi startup.

## Quick Installation

On your Raspberry Pi, run:

```bash
chmod +x install_service.sh
./install_service.sh
```

That's it! RoboCamara will now start automatically every time the Raspberry Pi boots.

## What Gets Installed

The installation script creates a systemd service that:
- Starts `main.py` automatically on boot
- Restarts the program if it crashes
- Runs in the background as a service
- Logs output to the system journal

## Managing the Service

### Check if the service is running:
```bash
sudo systemctl status robocamara
```

### Stop the service:
```bash
sudo systemctl stop robocamara
```

### Start the service:
```bash
sudo systemctl start robocamara
```

### Restart the service:
```bash
sudo systemctl restart robocamara
```

### Disable auto-start (service won't start on boot):
```bash
sudo systemctl disable robocamara
```

### Re-enable auto-start:
```bash
sudo systemctl enable robocamara
```

### View live logs:
```bash
sudo journalctl -u robocamara -f
```

### View recent logs:
```bash
sudo journalctl -u robocamara -n 50
```

## Manual Installation (if script doesn't work)

1. Edit `robocamara.service` and update paths if needed
2. Copy the service file:
   ```bash
   sudo cp robocamara.service /etc/systemd/system/
   ```
3. Reload systemd:
   ```bash
   sudo systemctl daemon-reload
   ```
4. Enable and start:
   ```bash
   sudo systemctl enable robocamara
   sudo systemctl start robocamara
   ```

## Troubleshooting

### Service fails to start
- Check logs: `sudo journalctl -u robocamara -n 50`
- Verify paths in `/etc/systemd/system/robocamara.service`
- Make sure `main.py` works manually: `python3 main.py`

### Camera not connecting
- Check if camera is connected: `gphoto2 --summary`
- Verify USB connection
- Check service logs for errors

### Uninstall
```bash
sudo systemctl stop robocamara
sudo systemctl disable robocamara
sudo rm /etc/systemd/system/robocamara.service
sudo systemctl daemon-reload
```
