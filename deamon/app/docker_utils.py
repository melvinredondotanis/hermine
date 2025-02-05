import docker
from flask import jsonify, request

from . import app, client, db


@app.route('/create/<image>', methods=['GET'])
def create_container(image):
    """Create container from an image."""
    try:
        if image not in client.images.list():
            try:
                client.images.pull(image)
            except docker.errors.ImageNotFound as err:
                return jsonify(str(err.explanation)), err.status_code
            except Exception as err:
                return jsonify(str(err)), 500

        container = client.containers.create(image)
        try:
            db.insert({'container_id': container.id})
            return jsonify({'container_id': container.id}), 201
        except Exception as err:
            container.remove(force=True)
            return jsonify(str(err)), 500
    except docker.errors.APIError as err:
        return jsonify(str(err.explanation)), err.status_code
    except Exception as err:
        return jsonify(str(err)), 500


@app.route('/start/<container_id>', methods=['GET'])
def start_container(container_id):
    """Start a created container."""
    try:
        container = client.containers.get(container_id)
        container.start()
        return jsonify({'success': True}), 200
    except docker.errors.APIError as err:
        return jsonify(str(err.explanation)), err.status_code
    except Exception as err:
        return jsonify(str(err)), 500


@app.route('/stop/<container_id>', methods=['GET'])
def stop_container(container_id):
    """Stop a running container."""
    try:
        container = client.containers.get(container_id)
        container.stop()
        return jsonify({'success': True}), 200
    except docker.errors.APIError as err:
        return jsonify(str(err.explanation)), err.status_code
    except Exception as err:
        return jsonify(str(err)), 500


@app.route('/pause/<container_id>', methods=['GET'])
def pause_container(container_id):
    """Pause a running container."""
    try:
        container = client.containers.get(container_id)
        container.pause()
        return jsonify({'success': True}), 200
    except docker.errors.APIError as err:
        return jsonify(str(err.explanation)), err.status_code
    except Exception as err:
        return jsonify(str(err)), 500


@app.route('/unpause/<container_id>', methods=['GET'])
def unpause_container(container_id):
    """Unpause a paused container."""
    try:
        container = client.containers.get(container_id)
        container.unpause()
        return jsonify({'success': True}), 200
    except docker.errors.APIError as err:
        return jsonify(str(err.explanation)), err.status_code
    except Exception as err:
        return jsonify(str(err)), 500


@app.route('/remove/<container_id>', methods=['DELETE'])
def remove_container(container_id):
    """Remove a container."""
    try:
        container = client.containers.get(container_id)
        container.remove(force=True)
        return jsonify({'success': True}), 200
    except docker.errors.APIError as err:
        return jsonify(str(err.explanation)), err.status_code
    except Exception as err:
        return jsonify(str(err)), 500


@app.route('/list', methods=['GET'])
def list_containers():
    """List all containers."""
    try:
        containers = client.containers.list(all=True)
        return jsonify({'containers': [container.id for container in containers]}), 200
    except docker.errors.APIError as err:
        return jsonify(str(err.explanation)), err.status_code
    except Exception as err:
        return jsonify(str(err)), 500


@app.route('/execute/<container_id>', methods=['POST'])
def exec_command(container_id):
    """Execute a command in a running container."""
    try:
        command = request.json.get('command')
        container = client.containers.get(container_id)
        result = container.exec_run(command)
        return jsonify({'stdout': result.output.decode()}), 200
    except docker.errors.APIError as err:
        return jsonify(str(err.explanation)), err.status_code
    except Exception as err:
        return jsonify(str(err)), 500
