#!/bin/bash

# Exit on error
set -e

echo "🚀 Deploying Healthcare Lifecycle Simulation..."

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f "healthcare_sim/.env" ]; then
    echo "⚙️ Creating .env file..."
    cp healthcare_sim/.env.example healthcare_sim/.env
    echo "⚠️ Please configure your .env file!"
fi

# Run tests if they exist
if [ -d "tests" ]; then
    echo "🧪 Running tests..."
    python -m pytest
fi

# Start the application
echo "🚀 Starting the application..."
streamlit run healthcare_sim/run.py 