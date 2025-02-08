# Sandbox API

A Flask-based REST API for managing Docker containers.

## Endpoints

### Create Container
- **URL**: `/sandbox/create/<image>`
- **Method**: `GET`
- **Path Parameters**: 
    - `image`: Docker image name
- **Success Response**: 
    - Code: 201
    - Content: `{"container_id": "<container_id>"}`

### Start Container
- **URL**: `/sandbox/start/<container_id>`
- **Method**: `GET`
- **Path Parameters**:
    - `container_id`: ID of the container
- **Success Response**:
    - Code: 200
    - Content: `{"success": true}`

### Stop Container
- **URL**: `/sandbox/stop/<container_id>`
- **Method**: `GET`
- **Path Parameters**:
    - `container_id`: ID of the container
- **Success Response**:
    - Code: 200
    - Content: `{"success": true}`

### Pause Container
- **URL**: `/sandbox/pause/<container_id>`
- **Method**: `GET`
- **Path Parameters**:
    - `container_id`: ID of the container
- **Success Response**:
    - Code: 200
    - Content: `{"success": true}`

### Unpause Container
- **URL**: `/sandbox/unpause/<container_id>`
- **Method**: `GET`
- **Path Parameters**:
    - `container_id`: ID of the container
- **Success Response**:
    - Code: 200
    - Content: `{"success": true}`

### Remove Container
- **URL**: `/sandbox/remove/<container_id>`
- **Method**: `DELETE`
- **Path Parameters**:
    - `container_id`: ID of the container
- **Success Response**:
    - Code: 200
    - Content: `{"success": true}`

### List Containers
- **URL**: `/sandbox/list`
- **Method**: `GET`
- **Success Response**:
    - Code: 200
    - Content: `{"containers": ["<container_id1>", "<container_id2>", ...]}`

### Container Status
- **URL**: `/sandbox/status/<container_id>`
- **Method**: `GET`
- **Path Parameters**:
    - `container_id`: ID of the container whose status is being requested
- **Success Response**:
    - Code: 200
    - Content: `{"status": "<container_status>"}`

### Execute Command
- **URL**: `/sandbox/execute/<container_id>`
- **Method**: `POST`
- **Path Parameters**:
    - `container_id`: ID of the container
- **Request Body**:
    ```json
    {
        "command": "<command_to_execute>"
    }
    ```
- **Success Response**:
    - Code: 200
    - Content: Command output stream

## Error Responses
- **Docker API Error**:
    - Code: Docker API specific error code
    - Content: `"<error_explanation>"`
- **Generic Error**:
    - Code: 500
    - Content: Error message string
