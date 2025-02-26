"""
This module serves as the main entry point for the Flask web server.
"""
import platform

from flask import Flask
from dotenv import dotenv_values
import distro

from api.sanbox import sandbox_bp
from api.system import system_bp
from api.history import history_bp


config = dotenv_values("/etc/hermine/env.cfg")

def process_modelfile():
    """
    Process the Modelfile by replacing specified words if the first line is '# False'.
    
    Returns:
        bool: True if processing completed successfully, False otherwise.
    """
    try:
        modelfile_path = "/etc/hermine/Modelfile"

        with open(modelfile_path, "rb") as file:
            raw_content = file.read()
            
        for encoding in ['utf-8', 'utf-16', 'latin-1']:
            try:
                content = raw_content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        replacements = {
            "NAME": distro.name() or 'unknown',
            "VERSION": distro.version() or 'n/a',
            "CODENAME":  distro.codename() or 'n/a',
            "KERNEL": platform.release(),
            "ARCHITECURE": platform.machine(),
            "HOST": platform.node()
        }

        modified_content = content
        for old_word, new_word in replacements.items():
            modified_content = modified_content.replace(old_word, new_word)
        
        if modified_content != content:
            with open(modelfile_path, "w") as file:
                file.write(modified_content)
        
        return True
    except Exception as e:
        print(f"Error processing Modelfile: {e}")
        return False


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
    app.register_blueprint(history_bp)
    app.run(
        debug=config["DEBUG"],
        host=config["HOST"],
        port=config["PORT"]
    )


if __name__ == "__main__":
    process_modelfile()
    main()
