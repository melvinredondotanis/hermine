"""
Hermine - A copilot for Linux
"""
import os
import sys
import math
import threading
import json
from typing import Tuple, List, Optional

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, GLib, Gdk, Gio  # pylint: disable=wrong-import-position
import cairo  # pylint: disable=wrong-import-position
import vlc  # pylint: disable=wrong-import-position
from openai import OpenAI  # pylint: disable=wrong-import-position

from voice_recorder import VoiceRecorder, RecorderConfig  # pylint: disable=wrong-import-position relative-beyond-top-level
from tts import TextToSpeechConverter  # pylint: disable=wrong-import-position relative-beyond-top-level
from stt import AudioTranscriber  # pylint: disable=wrong-import-position relative-beyond-top-level
from portal_dbus import DesktopPortal  # pylint: disable=wrong-import-position relative-beyond-top-level
from tools import search_file_and_get_urls, create_files # pylint: disable=wrong-import-position relative-beyond-top-level

APP_NAME = "Hermine"
APP_VERSION = "0.0.1"
APP_DESCRIPTION = "A Linux copilot"
APP_AUTHORS = ["Melvin Redondo--Tanis"]
APP_LICENSE = "Any"
APP_WEBSITE = "https://melvinredondotanis.github.io/hermine"
IS_RESIZABLE = False

CLIENT = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
PROMPT = """
            Vous êtes un assistant vocal pour le système Linux.
            \\ Votre nom est Hermine. Vous avez une connaissance approfondie
            \\ du système d'exploitation de l'utilisateur et pouvez fournir des
            \\ explications précises et efficaces.
        """
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Take a screenshot of the current screen"
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lock_session",
            "description": "Lock the current session"
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_file_and_get_urls",
            "description": "Search for files matching the pattern in the user's home directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename_pattern": {
                        "type": "string",
                        "description": "Search pattern for filenames"
                    }
                },
                "required": ["filename_pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_files",
            "description": "Create files with the given content",
            "parameters": {
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Name of the file"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "Content of the file"
                                }
                            },
                            "required": ["name", "content"]
                        }
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory path where files should be created"
                    }
                },
                "required": ["files"]
            }
        }
    }
]
DBUS_PORTAL = DesktopPortal()


FPS = 60
FRAME_DELAY_MS = int(1000 / FPS)
DEFAULT_ANIMATION_SPEED = 0.025
ACTIVATION_PROBABILITY = 0.002
ACTIVATION_DURATION_MS = 3000
PULSE_SPEED = 0.08

DEFAULT_SIZE = 300
PADDING = 20
NUM_SAMPLES = 120
NUM_RINGS = 20
BACKGROUND_COLOR = (
    0.15,
    0.15,
    0.15,
    1.0
    )


class Orb(Gtk.DrawingArea):
    """Interactive animated orb"""

    def __init__(self) -> None:
        super().__init__()
        self.set_size_request(DEFAULT_SIZE, DEFAULT_SIZE)
        self.connect('draw', self._on_draw)

        # Orb colors (blue, purple and pink shades)
        self.base_colors: List[Tuple[float, float, float]] = [
            (0.0, 0.44, 0.96),   # Blue
            (0.32, 0.23, 0.93),  # Blue-violet
            (0.56, 0.12, 0.85),  # Violet
            (0.82, 0.10, 0.56),  # Pink
            (0.28, 0.68, 0.96),  # Sky blue
        ]

        self.time: float = 0
        self.amplitude: float = 0.4
        self.active: bool = False
        self.pulse_state: float = 0

        GLib.timeout_add(FRAME_DELAY_MS, self._update_animation)

    def _update_animation(self) -> bool:
        """Update animation parameters and request redraw"""
        self.time += DEFAULT_ANIMATION_SPEED

        if self.active:
            self.pulse_state = (self.pulse_state + PULSE_SPEED) % (2 * math.pi)

        self.queue_draw()
        return True

    def activate(self) -> None:  # pylint: disable=arguments-differ
        """Activate the orb (start pulsing animation)"""
        self.active = True

    def _deactivate(self) -> bool:
        """Deactivate the orb (stop pulsing animation)"""
        self.active = False
        return False

    def _on_draw(self, widget: Gtk.DrawingArea, cr: 'cairo.Context') -> bool:  # pylint: disable=no-member
        """Render the orb"""
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()

        # Center and radius
        center_x = width / 2
        center_y = height / 2
        base_radius = min(width, height) / 2 - PADDING

        # Background
        cr.set_source_rgba(*BACKGROUND_COLOR)
        cr.paint()

        self._draw_orb(cr, center_x, center_y, base_radius)
        self._draw_glow(cr, center_x, center_y, base_radius)

        return False

    def _draw_orb(
        self,
        cr: 'cairo.Context',  # pylint: disable=no-member
        center_x: float,
        center_y: float,
        base_radius: float
        ) -> None:
        """Draw the animated orb with rings"""
        pulse = math.sin(self.pulse_state) * 0.2 if self.active else 0

        for ring in range(NUM_RINGS):
            radius_factor = 0.2 + 0.8 * (ring / (NUM_RINGS - 1))
        ring_radius = base_radius * radius_factor * (1.0 + pulse * (ring / NUM_RINGS))

        color = self._get_ring_color(ring)

        alpha = 0.8 if self.active else 0.6
        cr.set_source_rgba(*color, alpha * (0.2 + 0.8 * radius_factor))

        self._draw_wave_circle(cr, center_x, center_y, ring_radius, radius_factor)

        self._draw_glass_highlights(cr, center_x, center_y, base_radius)

    def _draw_glass_highlights(
        self,
        cr: 'cairo.Context',
        center_x: float,
        center_y: float,
        radius: float
        ) -> None:
        """Add glassy highlights to simulate reflections on glass surface"""
        highlight = cairo.RadialGradient(  # pylint: disable=no-member
        center_x - radius * 0.5, center_y - radius * 0.5, 0,
        center_x - radius * 0.5, center_y - radius * 0.5, radius * 0.8
        )
        highlight.add_color_stop_rgba(0, 1, 1, 1, 0.8)
        highlight.add_color_stop_rgba(0.3, 1, 1, 1, 0.3)
        highlight.add_color_stop_rgba(1, 1, 1, 1, 0)

        cr.set_source(highlight)
        cr.arc(center_x, center_y, radius, 0, 2 * math.pi)
        cr.fill()

    def _get_ring_color(self, ring: int) -> Tuple[float, float, float]:
        """Calculate interpolated color for a specific ring"""
        color_position = self.time / 2 + ring / 4
        color_idx = int(color_position) % len(self.base_colors)
        next_idx = (color_idx + 1) % len(self.base_colors)
        mix = color_position % 1.0

        c1 = self.base_colors[color_idx]
        c2 = self.base_colors[next_idx]

        return (
            c1[0] * (1-mix) + c2[0] * mix,
            c1[1] * (1-mix) + c2[1] * mix,
            c1[2] * (1-mix) + c2[2] * mix
        )

    def _draw_wave_circle(  # pylint: disable=too-many-arguments,too-many-positional-arguments
            self, cr: 'cairo.Context', center_x: float, center_y: float,  # pylint: disable=no-member
            radius: float, radius_factor: float) -> None:
        """Draw a wavy circle with animated distortions"""
        cr.move_to(
            center_x + radius * math.cos(0),
            center_y + radius * math.sin(0)
        )

        for i in range(1, NUM_SAMPLES + 1):
            angle = i * 2 * math.pi / NUM_SAMPLES

            wave = (math.sin(angle * 6 + self.time * 3) *
                   self.amplitude * (0.5 + 0.5 * math.sin(self.time)))
            wave += (math.sin(angle * 8 - self.time * 2) *
                    self.amplitude * 0.5)

            if self.active:
                wave *= 1.5

            r_factor = 1.0 + wave * 0.1 * radius_factor

            cr.line_to(
                center_x + radius * r_factor * math.cos(angle),
                center_y + radius * r_factor * math.sin(angle)
            )

        cr.close_path()
        cr.fill()

    def _draw_glow(
            self,
            cr: 'cairo.Context',  # pylint: disable=no-member
            center_x: float,
            center_y: float,
            base_radius: float
            ) -> None:
        """Draw central glow effect"""
        glow = cairo.RadialGradient(  # pylint: disable=no-member
            center_x, center_y, 0,
            center_x, center_y, base_radius * 0.7
        )
        glow.add_color_stop_rgba(0, 1, 1, 1, 0.6)
        glow.add_color_stop_rgba(0.5, 1, 1, 1, 0.1)
        glow.add_color_stop_rgba(1, 1, 1, 1, 0)

        cr.set_source(glow)
        cr.arc(center_x, center_y, base_radius * 0.7, 0, 2 * math.pi)
        cr.fill()


class HermineWindow(Gtk.ApplicationWindow):
    """Main application window with menus and orb"""

    def __init__(self, application: Gtk.Application) -> None:
        super().__init__(application=application, title="Hermine")
        self.set_resizable(IS_RESIZABLE)
        self.set_default_size(500, 500)
        self.set_position(Gtk.WindowPosition.CENTER)  # pylint: disable=no-member

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(self.main_box)  # pylint: disable=no-member

        config = RecorderConfig(output_file="hermine_recording.wav")
        self.voice_recorder = VoiceRecorder(config)
        self.recording_thread = None
        self.is_recording = False
        self.conversation_history = []

        self._create_menu()
        self._setup_orb()

    def _setup_orb(self) -> None:
        """Create and configure the orb"""
        self.orb = Orb()
        self.main_box.pack_start(self.orb, True, True, 0)  # pylint: disable=no-member

        self.orb.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)  # pylint: disable=no-member
        self.orb.connect("button-press-event", self._on_orb_clicked)

    def _create_menu(self) -> None:
        """Create the application menu bar"""
        menubar = Gtk.MenuBar()
        self.main_box.pack_start(menubar, False, False, 0)  # pylint: disable=no-member

        file_menu = self._create_menu_item("Files", menubar)
        self._create_menu_item(
            "Quit",
            file_menu.get_submenu(),
            callback=lambda _: self.get_application().quit()
        )

        info_menu = self._create_menu_item("Help", menubar)
        self._create_menu_item("About", info_menu.get_submenu(),
                               callback=self._show_about_dialog)

    def _create_menu_item(self, label: str, parent_menu: Gtk.MenuShell,
                          callback: Optional[callable] = None) -> Gtk.MenuItem:
        """Helper to create and attach menu items"""
        menu_item = Gtk.MenuItem(label=label)

        if isinstance(parent_menu, Gtk.MenuBar):
            submenu = Gtk.Menu()
            menu_item.set_submenu(submenu)
            parent_menu.append(menu_item)
        else:
            if callback:
                menu_item.connect("activate", callback)
            parent_menu.append(menu_item)

        return menu_item

    def _on_menu_item_clicked(self, _: Gtk.MenuItem) -> None:
        """Handle menu item clicks"""
        print("Menu item clicked")

    def _show_about_dialog(self, _: Gtk.MenuItem) -> None:
        """Show the about dialog"""
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_title("About")
        about_dialog.set_program_name(APP_NAME)
        about_dialog.set_version(APP_VERSION)
        about_dialog.set_comments(APP_DESCRIPTION)
        about_dialog.set_authors(APP_AUTHORS)
        about_dialog.set_license(APP_LICENSE)
        about_dialog.set_website(APP_WEBSITE)
        about_dialog.run()  # pylint: disable=no-member
        about_dialog.destroy()

    def _on_orb_clicked(self, widget: Orb, _: Gdk.Event) -> bool:
        """Toggle orb activation and recording on click"""
        if self.is_recording:
            widget.active = False
            self._stop_recording()
        else:
            widget.activate()
            self._start_recording()
        return True

    def _start_recording(self) -> None:
        """Start recording in a separate thread"""
        if self.is_recording:
            return

        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._recording_thread_function)
        self.recording_thread.daemon = True
        self.recording_thread.start()

    def _stop_recording(self) -> None:
        """Stop the current recording"""
        if self.is_recording:
            self.voice_recorder.stop_recording()
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(0.5)

    def _recording_thread_function(self) -> None:
        """Record audio and update UI when finished"""
        try:
            # Record audio continuously until stopped manually
            self.voice_recorder.record_continuously()

            GLib.idle_add(self._recording_finished)
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error during recording: {e}")
            GLib.idle_add(self._recording_finished)

    def _recording_finished(self) -> None:
        """Handle UI updates when recording is finished"""
        self.is_recording = False
        if self.orb.active:
            self.orb.active = False

        if not hasattr(self, 'conversation_history'):
            self.conversation_history = [
                {"role": "system", "content": PROMPT}
            ]

        threading.Thread(target=self._process_transcription, daemon=True).start()

    def _process_transcription(self) -> None:
        """Process audio transcription in a separate thread"""
        stt = AudioTranscriber()
        try:
            transcription = stt.transcribe_file("hermine_recording.wav")
            if transcription:
                GLib.idle_add(self._call_openai_api, transcription)
        except Exception as e: # pylint: disable=broad-exception-caught
            print(f"Error during transcription: {e}")

    def _call_openai_api(self, transcription: str) -> None:
        """Call OpenAI API in a separate thread"""
        self.conversation_history.append({"role": "user", "content": transcription})
        threading.Thread(target=self._execute_openai_call, daemon=True).start()

    def _execute_openai_call(self) -> None: # pylint: disable=too-many-branches
        """Execute the OpenAI API call in a separate thread"""
        completion = CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.conversation_history,
            tools=TOOLS
        )

        response_message = completion.choices[0].message

        if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                if tool_call.function.name == "take_screenshot":
                    DBUS_PORTAL.take_screenshot()
                elif tool_call.function.name == "lock_session":
                    DBUS_PORTAL.lock_session()
                elif tool_call.function.name == "search_file_and_get_urls":
                    args = json.loads(tool_call.function.arguments)
                    filename_pattern = args.get("filename_pattern")
                    print(f"Searching for files matching '{filename_pattern}'")
                    if filename_pattern:
                        results = search_file_and_get_urls(filename_pattern)
                        if results:
                            result_message = (f"Found files matching '{filename_pattern}':\n" +
                                              "\n".join(results))
                        else:
                            result_message = f"No files found matching '{filename_pattern}'"
                        self.conversation_history.append({
                            "role": "function", 
                            "name": "search_file_and_get_urls", 
                            "content": result_message
                        })
                elif tool_call.function.name == "create_files":
                    args = json.loads(tool_call.function.arguments)
                    files = args.get("files")
                    if files:
                        results = create_files(files)
                        if results:
                            result_message = ("Files created successfully:\n" +
                                              "\n".join(results))
                        else:
                            result_message = "Failed to create files"
                        self.conversation_history.append({
                            "role": "function", 
                            "name": "create_files", 
                            "content": result_message
                        })

        response_text = response_message.content or ""

        if response_text:
            self.conversation_history.append({"role": "assistant", "content": response_text})
            GLib.idle_add(self._generate_speech, response_text)

    def _generate_speech(self, text: str) -> None:
        """Generate speech in a separate thread"""
        threading.Thread(target=self._execute_speech_generation, args=(text,), daemon=True).start()

    def _execute_speech_generation(self, text: str) -> None:
        """Execute speech generation in a separate thread"""
        try:
            tts = TextToSpeechConverter()
            output_file = tts.generate_speech(text, "hermine_response.mp3")
            GLib.idle_add(self._play_audio, str(output_file))
        except Exception as e: # pylint: disable=broad-exception-caught
            print(f"Error during speech generation: {e}")

    def _play_audio(self, file_path: str) -> None:
        """Play the generated audio"""
        player = vlc.MediaPlayer(file_path)
        player.play()


class HermineApp(Gtk.Application):
    """Hermine application class"""

    def __init__(self) -> None:
        super().__init__(application_id="com.melvinredondotanis.hermine",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self) -> None: # pylint: disable=arguments-differ
        """Create and show the main window when the application is activated"""
        win = HermineWindow(application=self)
        win.connect("destroy", lambda _: self.quit())
        win.show_all()  # pylint: disable=no-member


if __name__ == "__main__":
        try:
            app = HermineApp()
            exit_status = app.run(sys.argv)
            sys.exit(exit_status)
        except (KeyboardInterrupt, EOFError, ValueError) as e:
            print(e)
            sys.exit(1)
