"""
Flask blueprint for managing chat history persistence and retrieval.
This module provides endpoints to create, retrieve, update, and delete chat sessions.
"""

import os
import json
import uuid
from datetime import datetime

from flask import Blueprint, jsonify, request


history_bp = Blueprint('history', __name__)
DB_FILE = "/etc/hermine/history_db.json"
chat_history = {}


def load_db(db_file=DB_FILE):
    """
    Load chat history from the JSON database file.
    
    Args:
        db_file: Path to the database file
        
    Returns:
        dict: Chat history data or empty dict if file doesn't exist or has errors
    """
    if not os.path.exists(db_file):
        return {}
    try:
        with open(db_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading database: {e}")
        return {}


def save_db(db, db_file=DB_FILE):
    """
    Save chat history to the JSON database file.
    
    Args:
        db: Chat history dictionary to save
        db_file: Path to the database file
    """
    os.makedirs(os.path.dirname(db_file), exist_ok=True)
    try:
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2)
    except IOError as e:
        print(f"Error saving database: {e}")


@history_bp.before_request
def load_history():
    """Load chat history from database before handling requests."""
    global chat_history
    chat_history = load_db()


@history_bp.after_request
def save_history(response):
    """Save chat history to database after handling requests."""
    save_db(chat_history)
    return response


@history_bp.route('/history/chats', methods=['GET'])
def get_all_chats():
    """Get a list of all chat IDs."""
    return jsonify(list(chat_history.keys()))


@history_bp.route('/history/chat', methods=['POST'])
def create_chat():
    """Create a new chat session with a unique ID."""
    chat_id = str(uuid.uuid4())
    chat_history[chat_id] = {"created_at": datetime.now().isoformat(), "messages": [], "container_id": None}
    return jsonify({"chat_id": chat_id})


@history_bp.route('/history/chat/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    """
    Get the content of a specific chat session.
    
    Args:
        chat_id: The unique ID of the chat to retrieve
    """
    if chat_id not in chat_history:
        return jsonify({"error": "Chat not found"}), 404
    return jsonify(chat_history[chat_id])


@history_bp.route('/history/chat/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """
    Delete a specific chat session.
    
    Args:
        chat_id: The unique ID of the chat to delete
    """
    if chat_id not in chat_history:
        return jsonify({"error": "Chat not found"}), 404
    del chat_history[chat_id]
    return jsonify({"success": True})


@history_bp.route('/history/chat/<chat_id>/message', methods=['POST'])
def add_message(chat_id):
    """
    Add a new message to a chat session.
    
    Args:
        chat_id: The unique ID of the chat to add the message to
    """
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


@history_bp.route('/history/chat/<chat_id>/container', methods=['POST'])
def update_chat_container(chat_id):
    """
    Associate a container ID with a chat session.
    
    Args:
        chat_id: The unique ID of the chat to update
    """
    if chat_id not in chat_history:
        return jsonify({"error": "Chat not found"}), 404
    data = request.get_json()
    if not data or 'container_id' not in data:
        return jsonify({"error": "Missing container_id"}), 400

    if isinstance(chat_history[chat_id], dict):
        chat_history[chat_id]['container_id'] = data['container_id']
    else:
        chat_history[chat_id] = {
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "container_id": data['container_id']
        }

    return jsonify({"success": True})
