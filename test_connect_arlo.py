#!/usr/bin/env python3

import os
import time
from dotenv import load_dotenv
from pyaarlo import PyArlo

# Load environment variables from .env file
# This includes USER_NAME, PASSWORD, CAMERA_NAME, and TFA credentials
load_dotenv()

# Connect to Arlo using PyArlo library
# This is a simple connection test that will verify:
# 1. Your Arlo credentials work
# 2. Your 2FA/MFA setup works if enabled
# 3. The camera specified in CAMERA_NAME is accessible
print("Connecting to Arlo...")
arlo = PyArlo(
    username=os.getenv("USER_NAME"),
    password=os.getenv("PASSWORD"),
    tfa_type="email",  # Using email for 2FA (could also be "sms")
    tfa_source="console",  # This requests manual entry of 2FA code in console
    # Note: We don't use IMAP (Gmail) automated 2FA here to ensure manual verification works
    save_state=True,
    wait_for_initial_setup=True,
)

# Look for the specific camera by name from your .env file
camera = arlo.lookup_camera_by_name(os.getenv("CAMERA_NAME"))

if camera:
    # Camera found - display basic information
    print(f"Found camera: {camera.name}")
    print(f"Device ID: {camera.device_id}")
    print(f"Serial Number: {camera.serial_number}")
    print(f"Battery Level: {camera.battery_level}%")
    print(f"Signal Strength: {camera.signal_strength}/5")

    # Get the last image URL (this is the most recent snapshot)
    print(f"Last Image URL: {camera.last_image}")

    # Request a new snapshot to verify camera is responsive
    print("Requesting new snapshot...")
    camera.request_snapshot()

    # Wait for snapshot to be taken - Arlo cameras take a moment to process
    print("Waiting 15 seconds for snapshot to be captured...")
    time.sleep(15)

    # Verify we received a new snapshot
    print(f"Updated Image URL: {camera.last_image}")

    # Print video info if available
    last_video = camera.last_video
    if last_video:
        print(f"Last Video: {last_video.created_at_pretty()}")
        print(f"Video URL: {last_video.url}")
else:
    # Camera not found - list available cameras to help troubleshoot
    print(f"Camera '{os.getenv('CAMERA_NAME')}' not found.")
    print("Available cameras:")
    for cam in arlo.cameras:
        print(f" - {cam.name}")
