#!/bin/bash
echo "Setting up Pravus.AI server..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

echo "Setup complete. You can now run the server with 'python app.py'"
echo ""
echo "To set your Deepseek API key, create a .env file with:"
echo "DEEPSEEK_API_KEY=your_api_key_here"
echo ""
echo "To run the server, use: python app.py" 