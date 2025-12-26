#!/bin/bash
# Setup script for Darvis Web Chat Interface
# Creates virtual environment and installs dependencies

echo "🔧 Setting up Darvis Web Chat Interface..."

# Create virtual environment if it doesn't exist
if [ ! -d "web_env" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv web_env
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source web_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📚 Installing Flask and dependencies..."
pip install flask flask-socketio

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the web chat interface:"
echo "   ./launch_web_chat.sh"
echo ""
echo "🌐 Then open http://localhost:5000 in your browser"