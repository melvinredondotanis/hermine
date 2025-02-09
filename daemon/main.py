"""
This module serves as the main entry point for the Flask web server.
"""

from flask import Flask
from dotenv import dotenv_values

from api.sanbox import sandbox_bp
from api.system import system_bp


config = dotenv_values(".env")


def main():
    """
    Entry point for the Flask application.

    This module serves as the main entry point for starting the Flask web server
    with configuration parameters defined in the config dictionary.

    :return: None
    """
    app = Flask(__name__)
    app.register_blueprint(sandbox_bp)
    app.register_blueprint(system_bp)
    app.run(
        debug=config["DEBUG"],
        host=config["HOST"],
        port=config["PORT"]
    )


if __name__ == "__main__":
    main()
