.PHONY: setup install run clean test-arlo

# Default target
all: setup run

# Set up virtual environment
setup:
	python -m venv venv

# Install dependencies
install: setup
	. venv/bin/activate && pip install -r requirements.txt

# Run the Lambda function locally (main functionality)
run:
	. venv/bin/activate && python lambda_function.py

# Simple test for Arlo connection only (for local development)
test-arlo:
	. venv/bin/activate && python test_connect_arlo.py

# Clean up pyc files and __pycache__ directories
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

# Full setup and install
setup-all: setup install 