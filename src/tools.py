"""
This module contains utility functions for the project.
"""
import os
import subprocess
import getpass
import webbrowser


def search_file_and_get_urls(filename_pattern, open_browser=True):
    """
    Quickly searches for files matching the pattern in the current user's home directory
    and returns URLs to these files.

    Args:
        filename_pattern: Search pattern for filenames

        open_browser: If True, opens the first result in the default browser

    Returns:
        List of URLs of matching files
    """
    username = getpass.getuser()
    home_dir = f"/home/{username}"
    cmd = ['find', home_dir, '-type', 'f', '-name', f'*{filename_pattern}*']

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        matches = []

        for file_path in result.stdout.strip().split('\n'):
            if file_path:
                url = f"file://{os.path.abspath(file_path)}"
                matches.append(url)

        if matches and open_browser:
            webbrowser.open(matches[0])

        return matches
    except (subprocess.SubprocessError, PermissionError, FileNotFoundError) as e:
        return e
