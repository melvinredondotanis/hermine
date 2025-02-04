from flask import Flask, request, jsonify
from .docker_utils import (
    create_container,
    start_container,
    stop_container,
    pause_container,
    unpause_container,
    remove_container,
    execute_command_in_container
)
from . import app


@app.route('/create/<image>', methods=['GET'])
def create(image):
    result = create_container(image)
    return jsonify(result)


@app.route('/start/<container_id>', methods=['GET'])
def start(container_id):
    result = start_container(container_id)
    return jsonify(result)


@app.route('/stop/<container_id>', methods=['GET'])
def stop(container_id):
    result = stop_container(container_id)
    return jsonify(result)


@app.route('/pause/<container_id>', methods=['GET'])
def pause(container_id):
    result = pause_container(container_id)
    return jsonify(result)


@app.route('/unpause/<container_id>', methods=['GET'])
def unpause(container_id):
    result = unpause_container(container_id)
    return jsonify(result)


@app.route('/remove/<container_id>', methods=['DELETE'])
def remove(container_id):
    result = remove_container(container_id)
    return jsonify(result)


@app.route('/execute', methods=['POST'])
def execute():
    data = request.json
    container_id = data.get('container_id')
    command = data.get('command')
    if not container_id or not command:
        return jsonify({'error': 'Container ID and command are required'}), 400

    result = execute_command_in_container(container_id, command)
    return jsonify(result)