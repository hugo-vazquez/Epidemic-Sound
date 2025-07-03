#!/bin/bash

# Set environmental variables
VENV_DIR="venv"
OKTA_DOMAIN="https://dev-04279224-admin.okta.com"
OKTA_API_TOKEN="00ta_mfskUB028k6X7EqBrDKWbqboefIFmTlSSUpXw"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv $VENV_DIR
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Install dependencies only if not already satisfied
echo "Checking dependencies..."
pip install --upgrade pip > /dev/null

if ! pip check > /dev/null 2>&1; then
  echo "Installing missing dependencies..."
  pip install -r requirements.txt
else
  echo "All requirements already satisfied."
fi

# Start the FastAPI app
echo "Starting FastAPI app with Uvicorn..."
uvicorn main:app --reload
