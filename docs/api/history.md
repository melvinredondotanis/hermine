# History API

## Description
The History API provides endpoints to manage chat history.

## Endpoints

### Get All Chats
- **URL**: `/history/chats`
- **Method**: `GET`
- **Description**: Retrieves a list of all chat IDs.
- **Success Response**:
    - Code: 200
    - Content: `["<chat_id1>", "<chat_id2>", ...]`
- **Error Response**:
    - Code: 500
    - Content: `{"error": "<error_message>"}`

### Create New Chat
- **URL**: `/history/chat`
- **Method**: `POST`
- **Description**: Creates a new chat and returns the chat ID.
- **Success Response**:
    - Code: 200
    - Content: `{"chat_id": "<new_chat_id>"}`
- **Error Response**:
    - Code: 500
    - Content: `{"error": "<error_message>"}`

### Get Chat
- **URL**: `/history/chat/<chat_id>`
- **Method**: `GET`
- **Path Parameters**:
    - `chat_id`: The ID of the chat to retrieve.
- **Description**: Retrieves the details of a specific chat.
- **Success Response**:
    - Code: 200
    - Content: `{"created_at": "<timestamp>", "messages": [{"user": "<user>", "message": "<message>", "timestamp": "<timestamp>"}]}`
- **Error Response**:
    - Code: 404
    - Content: `{"error": "Chat not found"}`
    - Code: 500
    - Content: `{"error": "<error_message>"}`

### Delete Chat
- **URL**: `/history/chat/<chat_id>`
- **Method**: `DELETE`
- **Path Parameters**:
    - `chat_id`: The ID of the chat to delete.
- **Description**: Deletes a specific chat.
- **Success Response**:
    - Code: 200
    - Content: `{"success": true}`
- **Error Response**:
    - Code: 404
    - Content: `{"error": "Chat not found"}`
    - Code: 500
    - Content: `{"error": "<error_message>"}`

### Add Message to Chat
- **URL**: `/history/chat/<chat_id>/message`
- **Method**: `POST`
- **Path Parameters**:
    - `chat_id`: The ID of the chat to add a message to.
- **Description**: Adds a message to a specific chat.
- **Success Response**:
    - Code: 200
    - Content: `{"success": true}`
- **Error Response**:
    - Code: 404
    - Content: `{"error": "Chat not found"}`
    - Code: 400
    - Content: `{"error": "Missing user or message"}`
    - Code: 500
    - Content: `{"error": "<error_message>"}`

### Update Chat Container
- **URL**: `/history/chat/<chat_id>/container`
- **Method**: `POST`
- **Path Parameters**:
    - `chat_id`: The ID of the chat to update.
- **Description**: Updates the container ID associated with a specific chat.
- **Success Response**:
    - Code: 200
    - Content: `{"success": true}`
- **Error Response**:
    - Code: 404
    - Content: `{"error": "Chat not found"}`
    - Code: 400
    - Content: `{"error": "Missing container_id"}`
    - Code: 500
    - Content: `{"error": "<error_message>"}`
