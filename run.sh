#!/bin/bash

VENV_DIR="venv"
export OKTA_DOMAIN="https://dev-04279224-admin.okta.com"
export OKTA_API_TOKEN="00ta_mfskUB028k6X7EqBrDKWbqboefIFmTlSSUpXw"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv $VENV_DIR
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Start the FastAPI app
echo "Starting FastAPI app with Uvicorn..."
uvicorn main:app --reload

