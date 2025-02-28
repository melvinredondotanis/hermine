"""
This module contains the routes for the system API.
"""

import platform
import subprocess

from flask import Blueprint, jsonify, request
import distro


system_bp = Blueprint('system', __name__)


@system_bp.route('/system/about', methods=['GET'])
def about():
    """
    Get information about the system.

    Returns:
        dict: System information
    """
    try:
        system_info = {
            'name': distro.name() or 'unknown',
            'version': distro.version() or 'n/a',
            'codename': distro.codename() or 'n/a',
            'kernel': platform.release(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
        }
    except (ValueError, TypeError, AttributeError) as e:
        return jsonify({'error': str(e)}), 500
    return jsonify(system_info), 200


@system_bp.route('/system/execute', methods=['POST'])
def execute():
    """
    Execute a command on the system.

    Returns:
        dict: Command output or error
    """
    data = request.get_json()
    command = data.get('command') if data else None
    if not command:
        return jsonify({'error': 'No command provided'}), 400
    try:
        output = subprocess.check_output(command, shell=True, text=True)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.output}), 500
    return jsonify({'output': output}), 200
