# Arlo Timelapse

A Python application to connect to Arlo cameras and create timelapses using the Arlo API.

## Features

- Connect to Arlo cameras using credentials
- Capture snapshots from cameras
- View camera status information
- Access to image and video URLs

## Setup

### Prerequisites

- Python 3.6+
- Arlo account credentials

### Installation

1. Clone this repository:

   ```
   git clone https://github.com/niklas/arlo-timelapse.git
   cd arlo-timelapse
   ```

2. Create a virtual environment:

   ```
   python -m venv venv
   ```

3. Activate the virtual environment:

   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
   - On Windows:
     ```
     venv\Scripts\activate
     ```

4. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file with your Arlo credentials:
   ```
   USER_NAME=your_arlo_email
   PASSWORD=your_arlo_password
   CAMERA_NAME=your_camera_name
   ```

## Usage

Run the script to connect to your Arlo camera:

```
python connect_arlo.py
```

## License

MIT
