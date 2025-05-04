# Arlo Timelapse

A Python application to connect to Arlo cameras and create timelapses of construction sites or other scenes using the Arlo API and AWS Lambda and storing image in s3.

## Table of Contents

- [Features](#features)
- [Development](#development)
- [Project Structure](#project-structure)
- [Setup](#setup)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Testing Locally](#testing-locally)
  - [Two-Factor Authentication via gmail (2FA)](#two-factor-authentication-via-gmail-2fa)
  - [AWS Lambda Setup](#aws-lambda-setup)
- [Quick Code Update & Redeployment Guide](#quick-code-update--redeployment-guide)
- [Downloading and Managing Images](#downloading-and-managing-images)
- [Creating Timelapses](#creating-timelapses)
- [Acknowledgements & Inspiration](#acknowledgements--inspiration)
- [License](#license)

## Features

- Using pyArlo
- Connect to Arlo cameras using credentials with MFA support
- Docker-based deployment for reliable Lambda compatibility
- Capture snapshots from cameras
- Schedule automatic snapshots via AWS Lambda and EventBridge
- Store images in S3 for easy timelapse creation

## Development

This project was developed using [Cursor](https://cursor.sh) IDE's agent mode with Claude 3.7 Sonnet.

For all API interactions with the Arlo cameras, we reference the `PyArlo-Docs.mdc` file, which contains documentation of the PyArlo library functions and their usage. This ensures consistent and correct usage of the Arlo API across the codebase.

## Project Structure

This project contains two main Python files:

- **lambda_function.py**: The main function deployed to AWS Lambda that:

  - Connects to Arlo using PyArlo with automated email-based 2FA (via IMAP)
  - Captures a snapshot from your configured camera
  - Uploads the snapshot to an S3 bucket with a timestamp
  - Designed to run on a schedule via EventBridge

- **test_connect_arlo.py**: A simple test script for local development that:
  - Tests basic connectivity to your Arlo account
  - Uses manual console-based 2FA (prompts you to enter the code)
  - Verifies the camera can be found and accessed
  - Checks basic camera information (battery, signal strength)
  - Requests a test snapshot to confirm camera operation

## Setup

### Prerequisites

- Python 3.6+
- Arlo account credentials
- Gmail account (for automated 2FA)
- AWS account (for Lambda and S3 setup)

### Installation

1. Clone this repository:

   ```
   git clone https://github.com/niklasingvar/arlo-timelapse.git
   cd arlo-timelapse
   ```

2. Create a virtual environment:

   ```
   python -m venv venv
   ```

3. Activate the virtual environment:

   ```
   source venv/bin/activate
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
   S3_BUCKET_NAME=my-arlo-timelapse-images
   # For automated 2FA via Gmail IMAP (required for lambda_function.py)
   TFA_USERNAME=your_gmail_address
   TFA_PASSWORD=your_gmail_app_password
   ```

   Note: The TFA credentials are only required for the full Lambda function test with automatic 2FA. The simple connectivity test will prompt you for the code manually.

### Testing Locally

This project provides two ways to test your setup locally:

1. Test Arlo connectivity with manual 2FA verification:

   ```
   make test-arlo
   ```

   This runs the `test_connect_arlo.py` script which will prompt you to enter a 2FA code from your email or phone. Use this first to verify your Arlo credentials work correctly.

2. Test the full Lambda function locally (with automatic Gmail IMAP 2FA):
   ```
   make run
   ```
   This runs the `lambda_function.py` script which uses automated IMAP-based 2FA and attempts to save a snapshot. This requires your TFA_USERNAME and TFA_PASSWORD to be properly configured in your .env file.

### Two-Factor Authentication via gmail (2FA)

Since Lambda functions run without user interaction, you need an automated way to handle Arlo's 2FA requirements. The PyArlo library supports automatic 2FA code retrieval via IMAP:

#### Setting Up Gmail for Automated 2FA

1. **IMAP in Gmail**:

   - Gmail now has IMAP permanently enabled by default (as of January 2025)
   - No configuration needed for IMAP access

2. **Create an App Password** (if your Gmail uses 2FA):

   - Go to your [Google Account](https://myaccount.google.com/)
   - Go to "Security" > "2-Step Verification"
   - Scroll down and click on "App passwords"
   - Select "Mail" as the app and "Other" as the device (name it "ArloLambdaTimeLapse")
   - Click "Generate"
   - Copy the 16-character password that appears (you'll use this in Lambda)

3. **Update Your Lambda Function Code**:

   - Modify the `lambda_function.py` to use IMAP for 2FA:

   ```python
   # In lambda_function.py
   arlo = PyArlo(
       username=username,
       password=password,
       tfa_type="email",
       tfa_source="imap",  # Use IMAP to fetch codes from email
       tfa_host="imap.gmail.com",
       tfa_username=os.getenv("TFA_USERNAME"),  # Gmail username
       tfa_password=os.getenv("TFA_PASSWORD"),  # Gmail app password
   )
   ```

4. **Add Environment Variables to Lambda**:

   - Go to AWS Lambda Console > Your Function > Configuration > Environment Variables
   - Add these new variables:
     - `TFA_USERNAME`: Your Gmail address (e.g., yourname@gmail.com)
     - `TFA_PASSWORD`: Your Gmail app password (the 16-character code)

5. **Update Your .env File** (for local testing):

   ```
   USER_NAME=your_arlo_email
   PASSWORD=your_arlo_password
   CAMERA_NAME=your_camera_name
   S3_BUCKET_NAME=my-arlo-timelapse-images
   TFA_USERNAME=your_gmail_address
   TFA_PASSWORD=your_gmail_app_password
   ```

6. **Update Your Lambda Deployment**:
   - Redeploy your Lambda function using the build_and_deploy.sh script

### AWS Lambda Setup

To automate snapshot collection for timelapses, you can deploy this script to AWS Lambda and schedule it to run 6 times per day.

### 1. Create an IAM User for AWS CLI Access

First, create an IAM user to manage your AWS resources from your local machine:

1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Click "Users" then "Create user"
3. Set a name (e.g., "arlo-timelapse-admin")
4. Enable "Provide user access to the AWS Management Console" (optional)
5. Under "Set permissions", attach the following policies:
   - AmazonS3FullAccess
   - AWSLambda_FullAccess
   - CloudWatchLogsFullAccess
6. Complete the user creation
7. On the success page, save the Access key ID and Secret access key (or download the CSV)
   - IMPORTANT: This is the only time AWS will show you the secret key
   - Download the CSV file or copy both keys immediately
   - Store these securely as they provide access to your AWS account

If you already have an IAM user and need to create new access keys:

1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Click on "Users" and select your user
3. Go to "Security credentials" tab
4. Under "Access keys", click "Create access key"
5. Choose "Command Line Interface (CLI)" and follow the prompts

Configure AWS CLI with your credentials:

```bash
aws configure
```

Enter your Access Key ID, Secret Access Key, preferred region, and output format.

**Output Format Options:**

- `json` (default) - Output in JSON format
- `text` - Output in plain text
- `table` - Output in ASCII table format
- `yaml` - Output in YAML format

For most users, the default `json` format is recommended.

#### Choosing an AWS Region

When prompted for a region, choose one closest to your physical location for best performance:

- North America: `us-east-1` (Virginia), `us-east-2` (Ohio), `us-west-1` (California), `us-west-2` (Oregon)
- Europe: `eu-west-1` (Ireland), `eu-central-1` (Frankfurt), `eu-west-2` (London)
- Asia Pacific: `ap-southeast-1` (Singapore), `ap-northeast-1` (Tokyo), `ap-southeast-2` (Sydney)

**Important:** All your AWS resources (Lambda, S3, etc.) should be in the same region to avoid cross-region data transfer costs and latency.

### 2. Create S3 Bucket

Create an S3 bucket to store your snapshots:

```bash
aws s3 mb s3://my-arlo-timelapse-images
```

Or through the AWS Console:

1. Go to [AWS S3 Console](https://s3.console.aws.amazon.com/)
2. Click "Create bucket"
3. Name your bucket (e.g., `my-arlo-timelapse-images`)
4. Choose your region and configure as needed
5. Click "Create bucket"

### 3. Prepare Lambda Deployment Package

You can prepare your Lambda deployment package in two ways:

#### Docker-Based Deployment

This approach ensures binary compatibility with the Lambda environment, especially for libraries with compiled components.

1. Create a Dockerfile:

   ```
   FROM public.ecr.aws/lambda/python:3.12

   # Copy requirements file
   COPY requirements.txt .

   # Install dependencies with specific platform tag to ensure compatibility
   RUN python -m pip install --platform=manylinux2014_x86_64 --target="${LAMBDA_TASK_ROOT}" --implementation=cp --only-binary=:all: --upgrade -r requirements.txt

   # Copy function code
   COPY lambda_function.py ${LAMBDA_TASK_ROOT}

   # Set the CMD to your handler
   CMD [ "lambda_function.lambda_handler" ]
   ```

2. Create a deployment script (build_and_deploy.sh):

   ```bash
   #!/bin/bash
   set -e

   echo "Building Docker image..."
   docker build -t arlo-lambda .

   echo "Creating container to extract files..."
   docker create --name arlo-temp arlo-lambda:latest
   mkdir -p docker-lambda

   echo "Copying Lambda package files from container..."
   docker cp arlo-temp:/var/task/. docker-lambda/
   docker rm arlo-temp

   echo "Creating deployment package..."
   cd docker-lambda
   zip -r ../lambda_deployment_docker.zip .
   cd ..

   echo "Updating Lambda function..."
   aws lambda update-function-code \
     --function-name arlo-snapshot-function \
     --zip-file fileb://lambda_deployment_docker.zip

   echo "Deployment completed"
   ```

3. Make the script executable and run it:
   ```bash
   chmod +x build_and_deploy.sh
   ./build_and_deploy.sh
   ```

This Docker-based approach ensures that native libraries and dependencies are compiled correctly for the Lambda environment, avoiding compatibility issues with libraries like cryptography.

### 4. Create IAM Role for Lambda

> **Note:** This is different from the IAM user "arlo-timelapse-admin" created earlier. The user is for your CLI access, while this role is what the Lambda service itself will use to access S3.

Create a role that gives Lambda permission to access S3:

1. Go to [IAM Roles](https://console.aws.amazon.com/iam/home#/roles)
2. Click "Create role"
3. Select "AWS service" as the trusted entity and "Lambda" as the service
4. Attach these policies:
   - AWSLambdaBasicExecutionRole (for CloudWatch Logs)
   - AmazonS3FullAccess (or create a custom policy for just your bucket)
5. Name the role (e.g., "arlo-lambda-s3-role") and create it

### 5. Create AWS Lambda Function

#### Finding Your AWS Account ID

Before creating the Lambda function, you need your AWS account ID:

1. Go to the [AWS Management Console](https://console.aws.amazon.com/)
2. Click on your username in the top-right corner
3. Your 12-digit account ID is shown in the dropdown menu
4. Alternatively, run this command: `aws sts get-caller-identity`

Create the Lambda function using AWS CLI:

NOTE: Replace `YOUR_ACCOUNT_ID` with your 12-digit AWS account ID and `YOUR_REGION` with your preferred region.

```bash
aws lambda create-function \
  --function-name arlo-snapshot-function \
  --runtime python3.9 \
  --handler lambda_function.lambda_handler \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/arlo-lambda-s3-role \
  --zip-file fileb://lambda_deployment.zip \
  --timeout 30 \
  --region YOUR_REGION \
  --environment "Variables={USER_NAME=your_arlo_email,PASSWORD=your_arlo_password,CAMERA_NAME=your_camera_name,S3_BUCKET_NAME=my-arlo-timelapse-images}"
```

Or through the AWS Console:

1. Go to [AWS Lambda Console](https://console.aws.amazon.com/lambda)
2. Click "Create function"
3. Select "Author from scratch"
4. Name your function (e.g., `arlo-snapshot-function`)
5. Select Python runtime (3.9 or newer)
6. Under "Permissions," select "Use an existing role" and choose the role you created
7. Click "Create function"
8. On the function page, upload your ZIP file (`lambda_deployment.zip`)

### 6. Configure Environment Variables

In the Lambda function configuration:

1. Go to "Configuration" > "Environment variables"
2. Add the following variables:
   - `USER_NAME`: Your Arlo account email
   - `PASSWORD`: Your Arlo account password
   - `CAMERA_NAME`: Name of your Arlo camera
   - `S3_BUCKET_NAME`: The name of your S3 bucket
   - `TFA_USERNAME`: Your Gmail address used for receiving 2FA codes
   - `TFA_PASSWORD`: Your Gmail app password (16-character code)

Note: For the TFA variables, refer to the "Two-Factor Authentication (2FA)" section below for detailed setup instructions.

### 7. Configure Trigger

1. Go to the [EventBridge Console](https://console.aws.amazon.com/events/)
2. Select **"EventBridge Schedule"** (not EventBridge Rule)
3. Click "Create schedule"
4. Configure the schedule:
   - Name: `arlo-snapshot-schedule`
   - For the cron expression, enter the following in the separate fields:
     - Minutes: `0`
     - Hours: `8,10,12,14,16,18`
     - Day of month: `*`
     - Month: `*`
     - Day of the week: `?`
     - Year: `*`
       (This runs at 8am, 10am, 12pm, 2pm, 4pm, and 6pm)
   - Select your time zone from the dropdown
5. Under Target details:

   - Select "AWS Lambda function" as the target
   - Select your "arlo-snapshot-function"
   - Leave the default version/alias settings
   - For execution role:
     - Select "Create new role for this schedule"
     - AWS will automatically create a role with the necessary permissions
     - This role will have a trust relationship allowing EventBridge Scheduler to assume it
     - It will also have permissions to invoke your Lambda function

   > Note: If you choose to use an existing role, it must have a trust relationship with EventBridge Scheduler (`scheduler.amazonaws.com`) and permissions to invoke your Lambda function.

6. Review and click "Create schedule"

This will create a schedule that automatically triggers your Lambda function at the specified times.

### Creating a Custom Execution Role (Optional)

If you prefer to create a custom role instead of using the automatically generated one:

1. Go to the [IAM Console](https://console.aws.amazon.com/iam/)
2. Select "Roles" → "Create role"
3. For trusted entity, select "AWS service" and choose "EventBridge Scheduler"
4. Attach the following policies:
   - `AWSLambdaRole` (or a custom policy that allows `lambda:InvokeFunction` on your specific function)
5. Name the role (e.g., `EventBridge-Scheduler-Arlo-Role`) and create it
6. Use this role when setting up your schedule

### 8. Test Your Function

1. Create a test event in the Lambda console
2. Click "Test" to verify your function works
3. Check your S3 bucket for the uploaded image

### 9. Monitoring Your Function

Check CloudWatch logs to see if your function is working:

```bash
aws logs filter-log-events --log-group-name /aws/lambda/arlo-snapshot-function
```

Or visit the CloudWatch Logs console and select the log group for your function.

## Quick Code Update & Redeployment Guide

If you're returning to the project and need to update the Lambda function:

1. ✅ Activate your virtual environment:

   ```
   source venv/bin/activate   # On macOS/Linux
   ```

2. ✅ Make your code changes to `lambda_function.py`

3. ✅ Test locally:

   ```
   make run
   ```

4. ✅ Rebuild and deploy using Docker:

   ```
   ./build_and_deploy.sh
   ```

5. ✅ Test the function in AWS Lambda console:
   - Go to AWS Lambda Console > Functions > arlo-snapshot-function
   - Click the "Test" tab at the top
   - Create a new test event if needed (empty JSON `{}` is fine)
   - Click "Test" button and wait for execution to complete
   - Check the execution results for success (status code 200)
6. ✅ Verify in CloudWatch logs:
   - Go to CloudWatch Console > Log groups > /aws/lambda/arlo-snapshot-function
   - Open the most recent log stream
   - Look for success messages like "Successfully uploaded snapshot\_\*.jpg to S3"
   - Check for any errors if the function failed

## Downloading and Managing Images

### Check for Images in S3

List all images in your bucket:

```bash
aws s3 ls s3://my-arlo-timelapse-images/
```

### Download All Images

Download all images to your local machine:

```bash
aws s3 sync s3://my-arlo-timelapse-images/ ./timelapse-images/
```

## Creating Timelapses

Once you have collected images in your S3 bucket, you can create a timelapse:

### Create Timelapse with FFmpeg

First, install FFmpeg:

```
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg
```

Then create the timelapse:

```
cd timelapse-images
ffmpeg -framerate 10 -pattern_type glob -i '*.jpg' -c:v libx264 -pix_fmt yuv420p timelapse.mp4
```

## Acknowledgements & Inspiration

This project was inspired by [arlo-timelapse-lambda](https://github.com/Notalifeform/arlo-timelapse-lambda) by Notalifeform, which provides a similar approach to creating timelapses with Arlo cameras. While no code was used from that project, it provided valuable insights into working with Arlo cameras and AWS Lambda integration.

Special thanks to the developers of the [PyArlo](https://github.com/jeffreydwalter/arlo) library, which makes interfacing with Arlo cameras possible. The `PyArlo-Docs.mdc` file has been an invaluable reference for understanding and implementing the Arlo API functionality in this project.

## License
