#!/bin/bash

echo "🏢 Tenant Management System - Installation Script"
echo "================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📋 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "To start the application:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run the application: python app.py"
echo "  3. Open your browser and go to: http://localhost:5000"
echo "  4. Login with: admin / 12345"
echo ""
echo "To deactivate the virtual environment when done: deactivate"