#!/usr/bin/env python3

import os
import time
from dotenv import load_dotenv
from pyaarlo import PyArlo

# Load environment variables
load_dotenv()

# Connect to Arlo
print("Connecting to Arlo...")
arlo = PyArlo(
    username=os.getenv("USER_NAME"),
    password=os.getenv("PASSWORD"),
    tfa_type="email",  # Or "sms" if you use text messages for 2FA
    tfa_source="console",  # Default method to get 2FA code
    save_state=True,
    wait_for_initial_setup=True,
)

# Look for the specific camera
camera = arlo.lookup_camera_by_name(os.getenv("CAMERA_NAME"))

if camera:
    print(f"Found camera: {camera.name}")
    print(f"Device ID: {camera.device_id}")
    print(f"Serial Number: {camera.serial_number}")
    print(f"Battery Level: {camera.battery_level}%")
    print(f"Signal Strength: {camera.signal_strength}/5")

    # Get the last image URL
    print(f"Last Image URL: {camera.last_image}")

    # Request a new snapshot
    print("Requesting new snapshot...")
    camera.request_snapshot()

    # Wait for snapshot to be taken
    time.sleep(15)

    print(f"Updated Image URL: {camera.last_image}")

    # Print video info if available
    last_video = camera.last_video
    if last_video:
        print(f"Last Video: {last_video.created_at_pretty()}")
        print(f"Video URL: {last_video.url}")
else:
    print(f"Camera '{os.getenv('CAMERA_NAME')}' not found.")
    print("Available cameras:")
    for cam in arlo.cameras:
        print(f" - {cam.name}")
