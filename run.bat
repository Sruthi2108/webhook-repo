@echo off
REM TechStax Assignment - Quick Setup Script for Windows
REM Run this script after setting up your .env file

echo 🚀 TechStax GitHub Webhook Setup
echo =================================

REM Check if .env exists
if not exist .env (
    echo ❌ .env file not found!
    echo Please create .env file with your MongoDB connection string
    echo Copy from .env.example and fill in your credentials
    pause
    exit /b 1
)

echo ✅ .env file found

REM Install dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

echo 🔍 Testing MongoDB connection...
python -c "import os; import pymongo; from dotenv import load_dotenv; load_dotenv(); client = pymongo.MongoClient(os.getenv('MONGO_URI')); client.admin.command('ping'); print('✅ MongoDB connection successful!')"

if errorlevel 1 (
    echo ❌ MongoDB connection failed!
    pause
    exit /b 1
)

echo 🌐 Starting Flask application...
echo 📡 Webhook endpoint will be available at: http://localhost:5000/webhook
echo 🎨 Dashboard will be available at: http://localhost:5000
echo 📊 Data API will be available at: http://localhost:5000/data
echo.
echo ⚡ Press Ctrl+C to stop the server
echo.

REM Start the Flask app
python app.py
