"""
Module for recording voice input from the microphone.
"""
import threading
from pathlib import Path
import wave
from dataclasses import dataclass

import pyaudio
import numpy as np


@dataclass
class RecorderConfig:
    """Configuration for voice recorder."""
    channels: int = 1
    rate: int = 16000
    chunk: int = 1024
    format: int = pyaudio.paInt16
    threshold: float = 0.01
    silence_timeout: float = 2.0
    output_file: str = "recording.wav"


class VoiceRecorder:
    """Records voice from microphone until silence is detected or manually stopped."""

    def __init__(self, config: RecorderConfig) -> None:
        """
        Initialize the voice recorder.

        Args:
            config: RecorderConfig object with recording parameters
        """
        self.config = config
        self.audio = pyaudio.PyAudio()
        self._stop_recording = threading.Event()

    def record_until_silence(self) -> str:
        """
        Record audio until silence is detected.

        Returns:
            Path to the recorded audio file.
        """
        frames = []

        stream = self.audio.open(
            format=self.config.format,
            channels=self.config.channels,
            rate=self.config.rate,
            input=True,
            frames_per_buffer=self.config.chunk
        )

        silence_counter = 0
        is_speaking = False

        print("Recording started - waiting for voice...")

        try:
            while not self._stop_recording.is_set():
                data = stream.read(self.config.chunk, exception_on_overflow=False)
                frames.append(data)

                audio_data = np.frombuffer(data, dtype=np.int16)
                volume = np.abs(audio_data).mean() / 32768.0

                if volume > self.config.threshold:
                    silence_counter = 0
                    if not is_speaking:
                        is_speaking = True
                        print("Voice detected - recording...")
                else:
                    if is_speaking:
                        silence_counter += 1
                        # Calculate silence threshold in frames
                        silence_threshold = int(
                            self.config.silence_timeout * self.config.rate / self.config.chunk
                        )
                        if silence_counter > silence_threshold:
                            break

        finally:
            stream.stop_stream()
            stream.close()

        return self._save_recording(frames)

    def record_continuously(self) -> str:
        """
        Record audio continuously until explicitly stopped.

        Returns:
            Path to the recorded audio file.
        """
        frames = []
        self._stop_recording.clear()

        stream = self.audio.open(
            format=self.config.format,
            channels=self.config.channels,
            rate=self.config.rate,
            input=True,
            frames_per_buffer=self.config.chunk
        )

        print("Recording started...")

        try:
            while not self._stop_recording.is_set():
                data = stream.read(self.config.chunk, exception_on_overflow=False)
                frames.append(data)

        finally:
            stream.stop_stream()
            stream.close()

        return self._save_recording(frames)

    def stop_recording(self) -> None:
        """Signal to stop the current recording."""
        self._stop_recording.set()

    def _save_recording(self, frames) -> str:
        """Save the recorded frames to a WAV file."""
        output_path = Path(self.config.output_file)

        # pylint: disable=no-member
        with wave.open(str(output_path), 'wb') as wf:
            wf.setnchannels(self.config.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.config.format))
            wf.setframerate(self.config.rate)
            wf.writeframes(b''.join(frames))
        # pylint: enable=no-member

        print(f"Recording saved to {output_path}")
        return str(output_path)

    def __del__(self) -> None:
        """Clean up resources."""
        self.audio.terminate()
