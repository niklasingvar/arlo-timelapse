#!/usr/bin/env python3

import os
import time
import boto3
import random
import string
from datetime import datetime
from dotenv import load_dotenv
from pyaarlo import PyArlo

# For local testing, load from .env file
# In Lambda, these will be environment variables
try:
    load_dotenv()
except:
    pass


def lambda_handler(event, context):
    """
    AWS Lambda handler function
    """
    # Get environment variables
    username = os.getenv("USER_NAME")
    password = os.getenv("PASSWORD")
    camera_name = os.getenv("CAMERA_NAME")
    bucket_name = os.getenv("S3_BUCKET_NAME")

    if not all([username, password, camera_name, bucket_name]):
        return {"statusCode": 500, "body": "Missing required environment variables"}

    try:
        # Connect to Arlo
        print("Connecting to Arlo...")
        arlo = PyArlo(
            username=username,
            password=password,
            tfa_type="email",  # Or "sms" if you use text messages for 2FA
            tfa_source="console",  # Default method to get 2FA code
            save_state=True,
            wait_for_initial_setup=True,
        )

        # Look for the specific camera
        camera = arlo.lookup_camera_by_name(camera_name)

        if not camera:
            print(f"Camera '{camera_name}' not found.")
            print("Available cameras:")
            for cam in arlo.cameras:
                print(f" - {cam.name}")
            return {"statusCode": 404, "body": f"Camera {camera_name} not found"}

        print(f"Found camera: {camera.name}")
        print(f"Battery Level: {camera.battery_level}%")

        # Request a new snapshot
        print("Requesting new snapshot...")
        camera.request_snapshot()

        # Wait for snapshot to be taken (Lambda has max 15 min timeout)
        time.sleep(15)

        # Get the image URL
        image_url = camera.last_image
        print(f"Image URL: {image_url}")

        if not image_url:
            return {"statusCode": 500, "body": "Failed to get image URL"}

        # Download the image
        import requests

        response = requests.get(image_url)
        if response.status_code != 200:
            return {
                "statusCode": response.status_code,
                "body": "Failed to download image",
            }

        # Generate a filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # Generate a random string instead of using uuid
        random_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        filename = f"snapshot_{timestamp}_{random_id}.jpg"

        # Save to S3
        s3_client = boto3.client("s3")
        s3_client.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=response.content,
            ContentType="image/jpeg",
        )

        print(f"Successfully uploaded {filename} to S3 bucket {bucket_name}")

        return {
            "statusCode": 200,
            "body": f"Successfully captured and stored snapshot: {filename}",
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"statusCode": 500, "body": f"Error: {str(e)}"}


# For local testing
if __name__ == "__main__":
    response = lambda_handler(None, None)
    print(response)
