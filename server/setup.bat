@echo off
echo Setting up Pravus.AI server...

rem Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

rem Activate virtual environment
call venv\Scripts\activate

rem Install requirements
echo Installing requirements...
pip install -r requirements.txt

echo Setup complete. You can now run the server with 'python app.py'
echo.
echo To set your Deepseek API key, create a .env file with:
echo DEEPSEEK_API_KEY=your_api_key_here
echo.
echo To run the server, use: python app.py 