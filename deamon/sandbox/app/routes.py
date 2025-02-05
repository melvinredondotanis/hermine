import docker
from flask import jsonify, request

from . import app, client


def _fetch_container(container_id):
    return client.containers.get(container_id)


@app.route('/create/<image>', methods=['GET'])
def create_container(image):
    try:
        if not any(image in img.tags for img in client.images.list()):
            try:
                client.images.pull(image)
            except docker.errors.ImageNotFound as e:
                return jsonify(str(e.explanation)), e.status_code
        container = client.containers.create(image, command=["sleep", "3600"])
        db.insert({'container_id': container.id})
        return jsonify({'container_id': container.id}), 201
    except docker.errors.APIError as e:
        return jsonify(str(e.explanation)), e.status_code
    except Exception as e:
        return jsonify(str(e)), 500


@app.route('/start/<container_id>', methods=['GET'])
def start_container(container_id):
    try:
        container = _fetch_container(container_id)
        container.restart()
        container.reload()
        return jsonify({'success': container.status == 'running'}), 200
    except docker.errors.APIError as e:
        return jsonify(str(e.explanation)), e.status_code
    except Exception as e:
        return jsonify(str(e)), 500


@app.route('/stop/<container_id>', methods=['GET'])
def stop_container(container_id):
    try:
        container = _fetch_container(container_id)
        container.stop()
        container.reload()
        return jsonify({'success': container.status == 'exited'}), 200
    except docker.errors.APIError as e:
        return jsonify(str(e.explanation)), e.status_code
    except Exception as e:
        return jsonify(str(e)), 500


@app.route('/pause/<container_id>', methods=['GET'])
def pause_container(container_id):
    try:
        _fetch_container(container_id).pause()
        return jsonify({'success': True}), 200
    except docker.errors.APIError as e:
        return jsonify(str(e.explanation)), e.status_code
    except Exception as e:
        return jsonify(str(e)), 500


@app.route('/unpause/<container_id>', methods=['GET'])
def unpause_container(container_id):
    try:
        _fetch_container(container_id).unpause()
        return jsonify({'success': True}), 200
    except docker.errors.APIError as e:
        return jsonify(str(e.explanation)), e.status_code
    except Exception as e:
        return jsonify(str(e)), 500


@app.route('/remove/<container_id>', methods=['DELETE'])
def remove_container(container_id):
    try:
        _fetch_container(container_id).remove(force=True)
        return jsonify({'success': True}), 200
    except docker.errors.APIError as e:
        return jsonify(str(e.explanation)), e.status_code
    except Exception as e:
        return jsonify(str(e)), 500


@app.route('/list', methods=['GET'])
def list_containers():
    try:
        containers = client.containers.list(all=True)
        return jsonify({'containers': [c.id for c in containers]}), 200
    except docker.errors.APIError as e:
        return jsonify(str(e.explanation)), e.status_code
    except Exception as e:
        return jsonify(str(e)), 500


@app.route('/execute/<container_id>', methods=['POST'])
def exec_command(container_id):
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
    except Exception as e:
        return jsonify(str(e)), 500
