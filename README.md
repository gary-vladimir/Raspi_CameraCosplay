# Raspi Camera Cosplay

A wearable functional camera cosplay that transforms a Canon Rebel T8i into an interactive photo booth experience with wireless sharing capabilities.

## Overview

This project creates a wearable camera cosplay that allows users to take photos with a large push button. The captured images are instantly displayed on an integrated monitor and can be shared wirelessly via a local hotspot network—perfect for outdoor events, conventions, or any location without WiFi infrastructure.

## Features

- **One-Button Photo Capture**: Large push button trigger for easy operation
- **Instant Display**: Photos immediately shown in full screen on integrated monitor
- **Wireless Sharing**: Local WiFi hotspot ("RoboCamara") for photo downloads
- **QR Code Access**: Users scan to connect and download their photos
- **No Internet Required**: Fully functional outdoors using local hotspot
- **Auto-Redirect**: Connected phones automatically open the photo download page

## How It Works

1. User presses the large push button mounted on the cosplay
2. Raspberry Pi triggers the Canon Rebel T8i camera via USB
3. Photo is captured and stored in a designated folder
4. Image is instantly displayed on the connected monitor in full screen
5. Flask server exposes the latest photo via local hotspot
6. Users scan QR code to connect to "RoboCamara" WiFi network
7. Browser automatically redirects to download page
8. New photos overwrite the previous one on the server

## Hardware Requirements

- Canon Rebel T8i camera
- Raspberry Pi Model B (2015)
- HDMI monitor
- Large push button
- Jumper wires
- Protoboard
- USB cable (camera to Raspberry Pi connection)
- Wireless Canon flash
- QR code display (for WiFi connection)

## Hardware Setup

See [images/connections.png](images/connections.png) for detailed diagrams showing:

- Raspberry Pi GPIO connections to the push button
- HDMI monitor connection
- Camera USB connection layout

## Project Inspiration

The design is modeled after the Canon Rebel T8i camera. See [images/vision.png](images/vision.png) for the reference image that inspired this project.

## Network Details

- **Hotspot Name**: RoboCamara
- **Type**: Local WiFi hotspot (no internet connection)
- **Server**: Flask-based web server
- **Access Method**: QR code scan for automatic connection
