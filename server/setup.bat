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
echo To set your Azure OpenAI configuration, create a .env file with:
echo AZURE_OPENAI_API_KEY=your_api_key_here
echo AZURE_OPENAI_ENDPOINT=your_endpoint_here
echo AZURE_OPENAI_API_VERSION=your_api_version_here
echo AZURE_OPENAI_CHAT_DEPLOYMENT=your_chat_deployment_here
echo AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your_embedding_deployment_here
echo.
echo To run the server, use: python app.py 