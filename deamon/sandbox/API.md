# Sandbox

A Flask-based REST API for managing Docker containers.

## Endpoints

### Create Container
- **URL**: `/create/<image>`
- **Method**: `GET`
- **Path Parameters**: 
    - `image`: Docker image name
- **Success Response**: 
    - Code: 201
    - Content: `{"container_id": "<container_id>"}`

### Start Container
- **URL**: `/start/<container_id>`
- **Method**: `GET`
- **Path Parameters**:
    - `container_id`: ID of the container
- **Success Response**:
    - Code: 200
    - Content: `{"success": true}`

### Stop Container
- **URL**: `/stop/<container_id>`
- **Method**: `GET`
- **Path Parameters**:
    - `container_id`: ID of the container
- **Success Response**:
    - Code: 200
    - Content: `{"success": true}`

### Pause Container
- **URL**: `/pause/<container_id>`
- **Method**: `GET`
- **Path Parameters**:
    - `container_id`: ID of the container
- **Success Response**:
    - Code: 200
    - Content: `{"success": true}`

### Unpause Container
- **URL**: `/unpause/<container_id>`
- **Method**: `GET`
- **Path Parameters**:
    - `container_id`: ID of the container
- **Success Response**:
    - Code: 200
    - Content: `{"success": true}`

### Remove Container
- **URL**: `/remove/<container_id>`
- **Method**: `DELETE`
- **Path Parameters**:
    - `container_id`: ID of the container
- **Success Response**:
    - Code: 200
    - Content: `{"success": true}`

### List Containers
- **URL**: `/list`
- **Method**: `GET`
- **Success Response**:
    - Code: 200
    - Content: `{"containers": ["<container_id1>", "<container_id2>", ...]}`

### Execute Command
- **URL**: `/execute/<container_id>`
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
