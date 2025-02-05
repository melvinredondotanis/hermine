"""
This module is the entry point of the application.
"""

from flask import Flask

import docker


app = Flask(__name__)
client = docker.from_env()
