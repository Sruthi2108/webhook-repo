# Test script to verify MongoDB connection and Flask setup
import os
import sys
from dotenv import load_dotenv
import pymongo
from datetime import datetime

def test_environment():
    """Test if environment is properly configured"""
    print("🔍 Testing Environment Configuration...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create .env file from .env.example")
        return False
    
    print("✅ .env file found")
    
    # Check MongoDB URI
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        print("❌ MONGO_URI not set in .env file")
        return False
    
    print("✅ MONGO_URI configured")
    
    return True

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("\n🗄️ Testing MongoDB Connection...")
    print("=" * 50)
    
    try:
        # Load environment variables
        load_dotenv()
        mongo_uri = os.getenv('MONGO_URI')
        
        # Connect to MongoDB
        client = pymongo.MongoClient(mongo_uri)
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Test database and collection access
        db = client['github_webhooks']
        collection = db['webhook_events']
        
        # Insert a test document
        test_doc = {
            'request_id': 'test_123',
            'author': 'test_user',
            'action': 'TEST',
            'from_branch': 'test',
            'to_branch': 'main',
            'timestamp': '4th July 2025 - 12:00 PM UTC',
            'test': True
        }
        
        result = collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Clean up test document
        collection.delete_one({'_id': result.inserted_id})
        print("✅ Test document cleaned up")
        
        # Close connection
        client.close()
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def test_flask_imports():
    """Test if Flask and required packages are installed"""
    print("\n📦 Testing Package Imports...")
    print("=" * 50)
    
    required_packages = [
        ('flask', 'Flask'),
        ('pymongo', 'PyMongo'),
        ('dotenv', 'python-dotenv'),
    ]
    
    all_good = True
    
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✅ {name} imported successfully")
        except ImportError:
            print(f"❌ {name} not installed")
            all_good = False
    
    if not all_good:
        print("\n📥 Install missing packages with:")
        print("pip install -r requirements.txt")
    
    return all_good

def main():
    """Run all tests"""
    print("🧪 TechStax Assignment - Environment Test")
    print("=" * 60)
    
    tests = [
        test_environment,
        test_flask_imports,
        test_mongodb_connection
    ]
    
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 All tests passed! Your environment is ready!")
        print("\n🚀 Next steps:")
        print("1. Run: python app.py")
        print("2. Open: http://localhost:5000")
        print("3. Set up GitHub webhooks")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
