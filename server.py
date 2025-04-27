import os
from flask import Flask, request, jsonify, render_template , redirect, url_for, session ,  send_file, send_from_directory,abort
from flask_socketio import SocketIO, emit, disconnect
from dotenv import load_dotenv
from flask_cors import CORS
from flask_mail import Mail, Message
import uuid
from datetime import datetime,timezone
import time
from pymongo import MongoClient, ReturnDocument
import base64
from datetime import datetime
from workflow_engine import  execute_workflow
from workflow_engine_nodes import node_categories
import re
load_dotenv()
from collections import defaultdict


# MongoDB Configuration (Update with your actual credentials)
MONGO_URI = os.getenv("MONGO_PUBLIC_URL")  # Replace with your MongoDB connection string
DATABASE_NAME = "chatbot"  # Replace with your database name
COLLECTION_REQUESTS = "requests"# Collection to store the form data
COLLECTION_CONVERSATIONS = "conversations"
db = ""
try:
    client = MongoClient(MONGO_URI)  # Initialize the MongoDB client
    db = client[DATABASE_NAME]  # Access the database
    requests_collection = db[COLLECTION_REQUESTS] # Access the collection
    conversations_collection = db[COLLECTION_CONVERSATIONS]
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    # Handle the error appropriately (e.g., exit the application)

allowed_origins = [
    "https://ai.nextgensell.com",
    "http://localhost:3000"
]

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": allowed_origins }})  # Enable CORS for your Flask routes

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret!')

# Configure Flask-Mail for Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True  # Change to True if using port 465
app.config['MAIL_USERNAME'] = 'botauto212@gmail.com'
app.config['MAIL_PASSWORD'] = 'cjeifgsiqfivevdx'  # Use your App Password
app.config['MAIL_DEFAULT_SENDER'] = 'botauto212@gmail.com'


mail = Mail(app)

socketio = SocketIO(app, cors_allowed_origins = allowed_origins )  # Allow all origins


workflows = [
    {
        "id": "1",
        "name": "Customer Onboarding",
        "description": "Process new customer applications and send welcome emails",
        "status": "active",
        "lastRun": "2 hours ago",
        "createdAt": "2023-04-01",
        "type": "standard",
        "folder": "Banking",
        "tags": ["Production", "Automated"],
        "environment": "PROD",
        "version": "1.2.0",
    },
    {
        "id": "2",
        "name": "Transaction Monitoring",
        "description": "Monitor transactions for suspicious activity",
        "status": "active",
        "lastRun": "5 minutes ago",
        "createdAt": "2023-03-15",
        "type": "standard",
        "folder": "Banking",
        "tags": ["Production", "Automated", "Critical"],
        "environment": "QA",
        "version": "2.0.1",
    },
    {
        "id": "3",
        "name": "Account Reconciliation",
        "description": "Daily account reconciliation process",
        "status": "inactive",
        "lastRun": "1 day ago",
        "createdAt": "2023-02-20",
        "type": "standard",
        "folder": "Banking",
        "tags": ["Production", "Automated"],
        "environment": "DEV",
        "version": "0.9.5",
    },
    {
        "id": "4",
        "name": "AI Data Processing",
        "description": "Process data from Google Sheets using AI models",
        "status": "active",
        "lastRun": "10 minutes ago",
        "createdAt": "2023-05-10",
        "type": "ai",
        "folder": "AI Workflows",
        "tags": ["Development", "AI"],
        "environment": "ETE",
        "version": "1.5.0",
    },
    {
        "id": "5",
        "name": "Customer Support AI",
        "description": "AI-powered customer support response generation",
        "status": "active",
        "lastRun": "1 hour ago",
        "createdAt": "2023-05-15",
        "type": "ai",
        "folder": "AI Workflows",
        "tags": ["Production", "AI"],
        "environment": "PROD",
        "version": "2.1.0",
    },
]

def generate_folders(workflows: list):
    folder_data = defaultdict(lambda: {"workflows": 0, "created_dates": []})
    for wf in workflows:
        name = wf["folder"]
        folder_data[name]["workflows"] += 1
        folder_data[name]["created_dates"].append(wf["createdAt"])
    folders = []
    for idx, (name, data) in enumerate(folder_data.items(), start=1):
        created_dates = data["created_dates"]
        created_at = min(created_dates)
        updated_at = max(created_dates)
        folders.append({
            "id": f"f{idx}",
            "name": name,
            "description": "",
            "workflows": data["workflows"],
            "parent": None,
            "createdAt": created_at,
            "updatedAt": updated_at
        })
    return folders




@app.route('/node-categories', methods=['GET'])
def get_node_categories():
    return jsonify(node_categories)

def now_iso():
    return datetime.utcnow().isoformat()

# Workflows endpoint
@app.route('/workflows', methods=['GET'])
def get_workflows():
    return jsonify(workflows)

@app.route('/workflows/<workflow_id>/move', methods=['PATCH'])
def move_workflow(workflow_id):
    data = request.get_json()
    folder_id = data.get('folderId')
    if not folder_id:
        abort(400, 'folderId required')
    wf = next((w for w in workflows if w['id'] == workflow_id), None)
    if not wf:
        abort(404, 'Workflow not found')
    wf['folder'] = folder_id
    wf['lastRun'] = now_iso()
    return jsonify(wf)

# Folders endpoints
@app.route('/folders', methods=['GET'])
def get_folders():
    folders = generate_folders(workflows)
    return jsonify(folders)

@app.route('/folders', methods=['POST'])
def create_folder():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    parent = data.get('parent', None)
    if not name:
        abort(400, 'name is required')
    new_id = str(uuid.uuid4())
    folder = {
        'id': new_id,
        'name': name,
        'description': description,
        'workflows': 0,
        'parent': parent,
        'createdAt': now_iso(),
        'updatedAt': now_iso(),
    }
    folders.append(folder)
    return jsonify(folder), 201

@app.route('/folders/<folder_id>', methods=['PUT'])
def update_folder(folder_id):
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    folder = next((f for f in folders if f['id'] == folder_id), None)
    if not folder:
        abort(404, 'Folder not found')
    if name:
        folder['name'] = name
    if description is not None:
        folder['description'] = description
    folder['updatedAt'] = now_iso()
    return jsonify(folder)

@app.route('/folders/<folder_id>', methods=['DELETE'])
def delete_folder(folder_id):
    global folders
    folder = next((f for f in folders if f['id'] == folder_id), None)
    if not folder:
        abort(404, 'Folder not found')
    # Remove folder
    folders = [f for f in folders if f['id'] != folder_id]
    # Optionally reassign child folders/workflows
    return jsonify({'message': 'Folder deleted'})




@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Authenticate the user (replace with real authentication logic)
        if username == "admin" and password == "password":
            session['logged_in'] = True
            return redirect(url_for('chatbot'))
        else:
            return "Invalid credentials", 401
    return render_template('login.html')


@app.route("/exec-workflow", methods=["GET", "POST"])
def runworkflow():
 return execute_workflow(request.json)


if __name__ == '__main__':
    print("WebSocket server started")
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
