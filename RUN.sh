#!/bin/bash

echo "========================================"
echo " GreenCloud Storage - Quick Start"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""

# Initialize database if not exists
if [ ! -f "database/greencloud.db" ]; then
    echo "Initializing database..."
    python init_db.py
    echo ""
fi

# Run the application
echo "Starting GreenCloud Server..."
echo ""
python app.py
