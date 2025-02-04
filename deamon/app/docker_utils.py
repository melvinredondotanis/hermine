from flask import jsonify
import docker

from . import client, app, db


@app.route('/create/<string:image>', methods=['GET'])
def create_container(image: str):
    try:
        if not image in client.images.list():
            try:
                client.images.pull(image)
            except docker.errors.ImageNotFound as e:
                return jsonify(str(e)), 404
        container = client.containers.create(image)
        db.insert({'container_id': container.id})
        return jsonify({'container_id': container.id}), 201
    except Exception as e:
        return jsonify(str(e)), 500


@app.route('/start/<string:container_id>', methods=['GET'])
def start_container(container_id: str):
    try:
        container = client.containers.get(container_id)
        container.start()
        return jsonify({'succes'}), 200
    except Exception as e:
        return jsonify(str(e)), 500


@app.route('/stop/<string:container_id>', methods=['GET'])
def stop_container(container_id):
    try:
        container = client.containers.get(container_id)
        container.stop()
        return jsonify({'succes'}), 200
    except Exception as e:
        return str(e)

@app.route('/pause/<container_id>', methods=['GET'])
def pause_container(container_id):
    try:
        container = client.containers.get(container_id)
        container.pause()
        return {'OK'}, 200
    except Exception as e:
        return str(e)

@app.route('/unpause/<container_id>', methods=['GET'])
def unpause_container(container_id):
    try:
        container = client.containers.get(container_id)
        container.unpause()
        return {'OK'}, 200
    except Exception as e:
        return str(e)

@app.route('/remove/<container_id>', methods=['DELETE'])
def remove_container(container_id):
    try:
        container = client.containers.get(container_id)
        container.remove(force=True)
        return {'OK'}, 200
    except Exception as e:
        return str(e)

@app.route('/execute', methods=['POST'])
def execute_command_in_container(container_id, command):
    try:
        container = client.containers.get(container_id)
        exec_result = container.exec_run(command)
        return {
            'stdout': exec_result.output.decode('utf-8')
        }
    except Exception as e:
        return str(e)
