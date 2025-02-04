import docker
from flask import Flask

app = Flask(__name__)
client = docker.from_env()
