"""
This module serves as the main entry point for the Flask web server.
"""

from dotenv import dotenv_values

from app.routes import app


config = dotenv_values(".env")


def main():
    """
    Entry point for the Flask application.

    This module serves as the main entry point for starting the Flask web server
    with configuration parameters defined in the config dictionary.

    Returns:
        None
    """
    app.run(
        debug=config["DEBUG"],
        host=config["HOST"],
        port=config["PORT"]
    )


if __name__ == "__main__":
    main()
