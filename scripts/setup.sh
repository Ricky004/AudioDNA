#!/bin/bash
set -e  # stop script on error

echo "🔧 Setting up environment..."

# Check if virtualenv is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 not found. Please install it first."
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "📥 Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠️ No requirements.txt found. Skipping..."
fi

echo "✅ Setup complete. To activate your environment later, run:"
echo "source venv/bin/activate"
