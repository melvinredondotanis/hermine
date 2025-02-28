# System API

## Description
The System API provides endpoints to retrieve system information and perform smart actions.

## Endpoints

### Get System Information
- **URL**: `/system/about`
- **Method**: `GET`
- **Description**: Retrieves information about the system.
- **Success Response**:
    - Code: 200
    - Content:
        ```json
        {
            "name": "<distro_name>",
            "version": "<distro_version>",
            "codename": "<distro_codename>",
            "kernel": "<kernel_version>",
            "architecture": "<system_architecture>",
            "hostname": "<system_hostname>"
        }
        ```
- **Error Response**:
    - Code: 500
    - Content: `{"error": "<error_message>"}`

### Perform Smart Action
- **URL**: `/system/action/<function>`
- **Method**: `GET`
- **Path Parameters**:
    - `function`: The name of the smart function to perform.
- **Description**: Calls a smart action function and returns the result.
- **Success Response**:
    - Code: 200
    - Content: Result of the smart function.
- **Error Response**:
    - Code: 500
    - Content: `{"error": "<error_message>"}`

### Execute Command
- **URL**: `/system/execute`
- **Method**: `POST`
- **Description**: Executes a system command.
- **Request Body**:
    - Content:
        ```json
        {
            "command": "<system_command>"
        }
        ```
- **Success Response**:
    - Code: 200
    - Content:
        ```json
        {
            "output": "<command_output>"
        }
        ```
- **Error Response**:
    - Code: 400
    - Content: `{"error": "No command provided"}`
    - Code: 500
    - Content: `{"error": "<error_message>"}`
