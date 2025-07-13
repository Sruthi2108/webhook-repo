#!/bin/bash

# TechStax Assignment - Quick Setup Script
# Run this script after setting up your .env file

echo "🚀 TechStax GitHub Webhook Setup"
echo "================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with your MongoDB connection string"
    echo "Copy from .env.example and fill in your credentials"
    exit 1
fi

echo "✅ .env file found"

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🔍 Testing MongoDB connection..."
python -c "
import os
import pymongo
from dotenv import load_dotenv

load_dotenv()
try:
    client = pymongo.MongoClient(os.getenv('MONGO_URI'))
    client.admin.command('ping')
    print('✅ MongoDB connection successful!')
except Exception as e:
    print(f'❌ MongoDB connection failed: {e}')
    exit(1)
"

echo "🌐 Starting Flask application..."
echo "📡 Webhook endpoint will be available at: http://localhost:5000/webhook"
echo "🎨 Dashboard will be available at: http://localhost:5000"
echo "📊 Data API will be available at: http://localhost:5000/data"
echo ""
echo "⚡ Press Ctrl+C to stop the server"
echo ""

# Start the Flask app
python app.py
