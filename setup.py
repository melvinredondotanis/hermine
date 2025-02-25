from setuptools import setup, find_packages
import os
import json
from setuptools.command.install import install


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        # Run standard install
        install.run(self)
        
        # Create config directory if it doesn't exist
        config_dir = '/etc/hermine'
        try:
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            # Create env.conf with default settings
            env_path = os.path.join(config_dir, 'env.conf')
            if not os.path.exists(env_path):
                with open(env_path, 'w') as f:
                    f.write("""# Hermine Configuration File
LOG_LEVEL=INFO
DEBUG=False
PORT=8080
HOST=127.0.0.1
""")
                print(f"Cr        # Add your dependencies here
eated {env_path}")
            
            # Create chat.json with default empty structure
            chat_path = os.path.join(config_dir, 'chat.json')
            if not os.path.exists(chat_path):
                with open(chat_path, 'w') as f:
                    default_chat = {
                        "settings": {
                            "default_model": "gpt-3.5-turbo",
                            "max_history": 10
                        },
                        "conversations": []
                    }
                    json.dump(default_chat, f, indent=4)
                print(f"Created {chat_path}")
                
        except PermissionError:
            print("Warning: Could not create config files in /etc/hermine due to permissions.")
            print("Try running the installation with sudo or create the files manually.")

setup(
    name="hermine",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
    ],
    cmdclass={
        'install': PostInstallCommand,
    },
    author="Melvin Redondo--Tanis",
    author_email="melvin@redondotanis.com",
    description="Hermine",
    keywords="hermine",
)
