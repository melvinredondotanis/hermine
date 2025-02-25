# History API Documentation

This document provides examples for using the Chat History API endpoints. All examples use cURL for demonstration purposes.

## Available Endpoints

### Chats Management

#### Get All Chats
```bash
curl -X GET http://localhost:5000/history/chats
```
Returns a list of all available chats.

#### Create a New Chat
```bash
curl -X POST http://localhost:5000/history/chat
```
Creates a new empty chat and returns its ID.

#### Get a Specific Chat
```bash
curl -X GET http://localhost:5000/history/chat/{chat_id}
```
Retrieves all messages and details for a specific chat.

#### Delete a Specific Chat
```bash
curl -X DELETE http://localhost:5000/history/chat/{chat_id}
```
Permanently deletes a chat and all its messages.

### Messages Management

#### Add a Message to a Chat
```bash
curl -X POST -H "Content-Type: application/json" \
    -d '{"user": "username", "message": "Hello, world!"}' \
    http://localhost:5000/history/chat/{chat_id}/message
```
Adds a new message to the specified chat.

## Note
Replace `{chat_id}` with an actual chat ID in the above examples.
