#!/bin/bash
# Quick build script for local development

echo "🎃 PumpkinScheduler Local Build Script"
echo "======================================"

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "🔧 Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Build executable
echo "🔨 Building executable..."
python build_exe.py

# Create release package
echo "📦 Creating release package..."
python create_release.py

echo ""
echo "🎉 Build complete!"
echo "📁 Executable: dist/PumpkinScheduler"
echo "📦 Release package: release/PumpkinScheduler-Release.zip"
