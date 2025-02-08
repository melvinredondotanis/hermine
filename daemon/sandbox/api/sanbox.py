"""
This module contains the routes for the sandbox API.
"""

import docker
from flask import jsonify, request

from . import app, client


def _fetch_container(container_id):
    """
    Fetch a container by its ID.

    :param container_id: The ID of the container.
    :return: The container.
    """
    return client.containers.get(container_id)


@app.route('/sandbox/create/<image>', methods=['GET'])
def create_container(image):
    """
    Create a new container.

    :param image: The image to use for the container.
    :return: The container ID.
    """
    try:
        if not any(image in img.tags for img in client.images.list()):
            try:
                client.images.pull(image)
            except docker.errors.ImageNotFound as e:
                return jsonify(str(e.explanation)), e.status_code
        container = client.containers.create(image, command=["sleep", "3600"])
        return jsonify({'container_id': container.id}), 201
    except docker.errors.APIError as e:
        return jsonify(str(e.explanation)), e.status_code
    except docker.errors.DockerException as e:
        return jsonify(str(e)), 500


@app.route('/sandbox/start/<container_id>', methods=['GET'])
def start_container(container_id):
    """
    Start a container.

    :param container_id: The ID of the container.
    :return: Whether the container is running.
    """
    try:
        container = _fetch_container(container_id)
        container.restart()
        container.reload()
        return jsonify({'success': container.status == 'running'}), 200
    except docker.errors.APIError as e:
        return jsonify(str(e.explanation)), e.status_code
    except docker.errors.DockerException as e:
        return jsonify(str(e)), 500


@app.route('/sandbox/stop/<container_id>', methods=['GET'])
def stop_container(container_id):
    """
    Stop a container.

    :param container_id: The ID of the container.
    :return: Whether the container is stopped.
    """
    try:
        container = _fetch_container(container_id)
        container.stop()
        container.reload()
        return jsonify({'success': container.status == 'exited'}), 200
    except docker.errors.APIError as e:
        return jsonify(str(e.explanation)), e.status_code
    except docker.errors.DockerException as e:
        return jsonify(str(e)), 500


@app.route('/sandbox/pause/<container_id>', methods=['GET'])
def pause_container(container_id):
    """
    Pause a container.

    :param container_id: The ID of the container.
    :return: Whether the container is paused.
    """
    try:
        _fetch_container(container_id).pause()
        return jsonify({'success': True}), 200
    except docker.errors.APIError as e:
        return jsonify(str(e.explanation)), e.status_code
    except docker.errors.DockerException as e:
        return jsonify(str(e)), 500


@app.route('/sandbox/unpause/<container_id>', methods=['GET'])
def unpause_container(container_id):
    """
    Unpause a container.

    :param container_id: The ID of the container.
    :return: Whether the container is unpaused.
    """
    try:
        _fetch_container(container_id).unpause()
        return jsonify({'success': True}), 200
    except docker.errors.APIError as e:
        return jsonify(str(e.explanation)), e.status_code
    except docker.errors.DockerException as e:
        return jsonify(str(e)), 500


@app.route('/sandbox/remove/<container_id>', methods=['DELETE'])
def remove_container(container_id):
    """
    Remove a container.

    :param container_id: The ID of the container.
    :return: Whether the container is removed.
    """
    try:
        _fetch_container(container_id).remove(force=True)
        return jsonify({'success': True}), 200
    except docker.errors.APIError as e:
        return jsonify(str(e.explanation)), e.status_code
    except docker.errors.DockerException as e:
        return jsonify(str(e)), 500


@app.route('/sandbox/list', methods=['GET'])
def list_containers():
    """
    List all containers.

    :return: The list of container IDs.
    """
    try:
        containers = client.containers.list(all=True)
        return jsonify({'containers': [c.id for c in containers]}), 200
    except docker.errors.APIError as e:
        return jsonify(str(e.explanation)), e.status_code
    except docker.errors.DockerException as e:
        return jsonify(str(e)), 500


@app.route('/sandbox/status/<container_id>', methods=['GET'])
def container_status(container_id):
    """
    Get the status of a container.

    :param container_id: The ID of the container.
    :return: The status of the container.
    """
    try:
        container = _fetch_container(container_id)
        return jsonify({'status': container.status}), 200
    except docker.errors.APIError as e:
        return jsonify(str(e.explanation)), e.status_code
    except docker.errors.DockerException as e:
        return jsonify(str(e)), 500


@app.route('/sandbox/execute/<container_id>', methods=['POST'])
def exec_command(container_id):
    """
    Execute a command in a container.

    :param container_id: The ID of the container.
    :return: The output of the command.
    """
    try:
        command = request.json.get('command')
        exec_result = _fetch_container(container_id).exec_run(
            command, stream=True
        )

        def generate():
            for chunk in exec_result.output:
                yield chunk.decode(errors='replace')

        return app.response_class(generate(), mimetype='text/plain')
    except docker.errors.APIError as e:
        return jsonify(str(e.explanation)), e.status_code
    except docker.errors.DockerException as e:
        return jsonify(str(e)), 500
