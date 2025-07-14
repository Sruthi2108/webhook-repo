from flask import Flask, request, jsonify, render_template
import pymongo
from datetime import datetime
import hashlib
import hmac
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)

# MongoDB Configuration
MONGO_URI = "mongodb+srv://sruthig509:qJgNHHIpHRBnjnMW@cluster0.b1hezbs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = 'github_webhooks'
COLLECTION_NAME = 'webhook_events'

# GitHub Webhook Secret (optional for security)
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '')

# Initialize MongoDB connection
try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print(f"❌ MongoDB connection error: {e}")
    collection = None

def verify_signature(payload_body, signature_header):
    if not WEBHOOK_SECRET:
        return True
    if signature_header is None:
        return False
    sha_name, signature = signature_header.split('=')
    if sha_name != 'sha256':
        return False
    mac = hmac.new(WEBHOOK_SECRET.encode(), payload_body, hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)

def format_timestamp(iso_timestamp):
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        day = dt.day
        if 10 <= day % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return dt.strftime(f"{day}{suffix} %B %Y - %I:%M %p UTC")
    except Exception as e:
        print(f"Error formatting timestamp: {e}")
        return iso_timestamp

def process_push_event(payload):
    try:
        if 'head_commit' not in payload or not payload['head_commit']:
            print("⚠️ No head_commit found.")
            return None
        commit_hash = payload['head_commit']['id']
        author = payload['pusher']['name']
        to_branch = payload['ref'].split('/')[-1]
        timestamp = format_timestamp(payload['head_commit']['timestamp'])
        data = {
            'request_id': commit_hash,
            'author': author,
            'action': 'PUSH',
            'from_branch': to_branch,
            'to_branch': to_branch,
            'timestamp': timestamp
        }
        print("✅ Processed push event:", json.dumps(data, indent=2))
        return data
    except Exception as e:
        print(f"❌ Error processing push event: {e}")
        return None

def process_pull_request_event(payload):
    try:
        pr_data = payload['pull_request']
        pr_id = str(pr_data['id'])
        author = pr_data['user']['login']
        from_branch = pr_data['head']['ref']
        to_branch = pr_data['base']['ref']
        if pr_data.get('merged', False):
            action = 'MERGE'
            timestamp = format_timestamp(pr_data['merged_at'])
        else:
            action = 'PULL_REQUEST'
            timestamp = format_timestamp(pr_data['created_at'])
        return {
            'request_id': pr_id,
            'author': author,
            'action': action,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp
        }
    except Exception as e:
        print(f"Error processing pull request event: {e}")
        return None

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Template rendering error: {e}", 500

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        payload = request.get_json()
        print("📦 Raw Payload:", json.dumps(payload, indent=2))
        signature = request.headers.get('X-Hub-Signature-256')
        event_type = request.headers.get('X-GitHub-Event')
        print(f"📨 Received {event_type} event")
        if not verify_signature(request.data, signature):
            return jsonify({'error': 'Invalid signature'}), 401
        event_data = None
        if event_type == 'push':
            event_data = process_push_event(payload)
        elif event_type == 'pull_request':
            event_data = process_pull_request_event(payload)
        else:
            print(f"⚠️ Unsupported event type: {event_type}")
            return jsonify({'message': 'Event type not supported'}), 200
        if event_data:
            result = collection.insert_one(event_data)
            print(f"✅ Stored event in MongoDB with ID: {result.inserted_id}")
            count = collection.count_documents({})
            print("📊 Total documents after insert:", count)

            return jsonify({'message': 'Webhook processed successfully', 'id': str(result.inserted_id)}), 200
        else:
            return jsonify({'error': 'Failed to process event data'}), 400
    except Exception as e:
        print(f"❌ Webhook processing error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/data')
def get_data():
    try:
        events = list(collection.find().sort('_id', -1).limit(50))
        for event in events:
            event['_id'] = str(event['_id'])
        return jsonify(events)
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return jsonify({'error': 'Failed to fetch data'}), 500

@app.route('/health')
def health_check():
    try:
        client.admin.command('ping')
        return jsonify({
            'status': 'healthy',
            'mongodb': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'mongodb': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/debug-insert')
def debug_insert():
    try:
        if collection is not None:
            event = {
                "request_id": "test123",
                "author": "TestUser",
                "action": "PUSH",
                "from_branch": "main",
                "to_branch": "main",
                "timestamp": "14th July 2025 - 5:30 PM UTC"
            }
            result = collection.insert_one(event)
            return jsonify({
                'message': 'Test event inserted successfully',
                'id': str(result.inserted_id),
                'request_id': event['request_id']
            }), 200
        else:
            return jsonify({'error': 'No DB connection.'}), 500
    except Exception as e:
        print(f"❌ Debug Insert Error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("🚀 Starting GitHub Webhook Flask App...")
    print("📡 Webhook endpoint: /webhook")
    print("🌐 UI available at: /")
    print("📊 Data API: /data")
    print("❤️ Health check: /health")
    app.run(debug=False, host='0.0.0.0', port=5000)
