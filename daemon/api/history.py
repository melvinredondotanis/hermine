import json
import os
import uuid
from datetime import datetime
from flask import Blueprint, jsonify, request

history_bp = Blueprint('history', __name__)
DB_FILE = '/home/melvin/Documents/Repositorys/hermine/daemon/api/history_db.json'

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

@history_bp.before_request
def load_history():
    global chat_history
    chat_history = load_db()

@history_bp.after_request
def save_history(response):
    save_db(chat_history)
    return response

@history_bp.route('/history/chats', methods=['GET'])
def get_all_chats():
    return jsonify(list(chat_history.keys()))

@history_bp.route('/history/chat', methods=['POST'])
def create_chat():
    chat_id = str(uuid.uuid4())
    chat_history[chat_id] = {"created_at": datetime.now().isoformat(), "messages": []}
    return jsonify({"chat_id": chat_id})

@history_bp.route('/history/chat/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    if chat_id not in chat_history:
        return jsonify({"error": "Chat not found"}), 404
    return jsonify(chat_history[chat_id])

@history_bp.route('/history/chat/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    if chat_id not in chat_history:
        return jsonify({"error": "Chat not found"}), 404
    del chat_history[chat_id]
    return jsonify({"success": True})

@history_bp.route('/history/chat/<chat_id>/message', methods=['POST'])
def add_message(chat_id):
    if chat_id not in chat_history:
        return jsonify({"error": "Chat not found"}), 404
    data = request.get_json()
    if not data or 'user' not in data or 'message' not in data:
        return jsonify({"error": "Missing user or message"}), 400
    chat_history[chat_id]['messages'].append({
        "user": data['user'],
        "message": data['message'],
        "timestamp": datetime.now().isoformat()
    })
    return jsonify({"success": True})
