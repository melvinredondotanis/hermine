"""
This module contains the routes for the system API.
"""

import platform

from flask import Blueprint, jsonify
import distro


system_bp = Blueprint('system', __name__)


@system_bp.route('/system/about', methods=['GET'])
def about():
    """
    Get information about the system.

    :return: Information about the system.
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
