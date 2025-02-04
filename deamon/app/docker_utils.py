import docker

from . import client


def create_container(image):
    try:
        container = client.containers.create(image)
        return {'container_id': container.id}, 201
    except Exception as e:
        return str(e)


def start_container(container_id):
    try:
        container = client.containers.get(container_id)
        container.start()
        return {'OK'}, 200
    except Exception as e:
        return str(e)


def stop_container(container_id):
    try:
        container = client.containers.get(container_id)
        container.stop()
        return {'OK'}, 200
    except Exception as e:
        return str(e)


def pause_container(container_id):
    try:
        container = client.containers.get(container_id)
        container.pause()
        return {'OK'}, 200
    except Exception as e:
        return str(e)


def unpause_container(container_id):
    try:
        container = client.containers.get(container_id)
        container.unpause()
        return {'OK'}, 200
    except Exception as e:
        return str(e)


def remove_container(container_id):
    try:
        container = client.containers.get(container_id)
        container.remove(force=True)
        return {'OK'}, 200
    except Exception as e:
        return str(e)


def execute_command_in_container(container_id, command):
    try:
        container = client.containers.get(container_id)
        exec_result = container.exec_run(command)
        return {
            'stdout': exec_result.output.decode('utf-8')
        }
    except Exception as e:
        return str(e)
