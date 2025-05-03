FROM public.ecr.aws/lambda/python:3.12

# Copy requirements file
COPY requirements.txt .

# Install dependencies with specific platform tag to ensure compatibility
RUN python -m pip install --platform=manylinux2014_x86_64 --target="${LAMBDA_TASK_ROOT}" --implementation=cp --only-binary=:all: --upgrade -r requirements.txt

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "lambda_function.lambda_handler" ] 