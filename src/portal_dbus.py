"""
This script demonstrates how to interact with the Desktop portal using D-Bus
in Python.
"""
import pydbus
from gi.repository import GLib


class DesktopPortal:
    """
    Class for interacting with the Desktop portal
    """

    def __init__(self):
        self.bus = pydbus.SessionBus()
        self.desktop_path = "/org/freedesktop/portal/desktop"
        self.desktop_iface = "org.freedesktop.portal.Desktop"

        # Get the desktop portal object
        self.desktop = self.bus.get(self.desktop_iface, self.desktop_path)

        # Get the interfaces
        self.screenshot = self.desktop["org.freedesktop.portal.Screenshot"]
        
        # Get the screensaver interface
        self.screensaver = self.bus.get("org.gnome.ScreenSaver", "/org/gnome/ScreenSaver")

    def take_screenshot(
            self,
            interactive=False,
            capture_cursor=False,
            parent_window=""
            ):
        """Take a screenshot"""
        try:
            options = {
                "interactive": GLib.Variant('b', interactive),
                "cursor": GLib.Variant('b', capture_cursor)
                }
            return self.screenshot.Screenshot(parent_window, options)
        except Exception as e:
            return e
            
    def lock_session(self):
        """Lock the screen using GNOME Screensaver"""
        try:
            self.screensaver.Lock()
            return True
        except Exception as e:
            return e


if __name__ == "__main__":
    portal = DesktopPortal()

    result = portal.take_screenshot()
    print(result)
