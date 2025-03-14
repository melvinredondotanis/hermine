"""
Voice recording module with automatic silence detection.
"""
import wave
from dataclasses import dataclass
from typing import List

import numpy as np
import sounddevice as sd


@dataclass
class RecorderConfig:
    """Configuration parameters for voice recording."""
    output_file: str = "output.wav"
    sample_rate: int = 44100
    channels: int = 1
    chunk_size: int = 1024
    silence_threshold: int = 5000
    format_type: str = 'int16'
    silence_timeout: float = 2.0


class VoiceRecorder: # pylint: disable=too-many-instance-attributes)
    """Records audio when voice is detected and stops on silence."""

    def __init__(self, config: RecorderConfig = None) -> None:
        """
        Initialize the voice recorder with configurable parameters.

        Args:
            config: Configuration parameters for recording
        """
        self.config = config or RecorderConfig()
        self.output_file = self.config.output_file
        self.sample_rate = self.config.sample_rate
        self.channels = self.config.channels
        self.chunk_size = self.config.chunk_size
        self.silence_threshold = self.config.silence_threshold
        self.format_type = self.config.format_type
        self.silence_timeout = self.config.silence_timeout


    def _detect_voice(self, indata: np.ndarray) -> bool:
        """
        Determine if voice is present in audio data.

        Args:
            indata: Audio data as numpy array

        Returns:
            True if voice is detected, False if silence
        """
        volume = np.linalg.norm(indata) * 10
        return volume > self.silence_threshold

    def record_until_silence(self) -> str:
        """
        Record audio until silence is detected.

        Returns:
            Path to the saved audio file

        Raises:
            RuntimeError: If recording or saving fails
        """
        frames: List[np.ndarray] = []
        recording = False

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.format_type
            ) as stream:
                while True:
                    data, _ = stream.read(self.chunk_size)

                    if self._detect_voice(data):
                        if not recording:
                            recording = True
                        frames.append(data)
                    elif recording:
                        break

            return self._save_to_file(frames)
        except Exception as err:
            raise RuntimeError(f"Failed to record audio: {err}") from err

    def update_config(self, **kwargs) -> None:
        """
        Update recorder configuration parameters.

        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                setattr(self, key, value)

    def _save_to_file(self, frames: List[np.ndarray]) -> str:
        """
        Save recorded audio frames to WAV file.

        Args:
            frames: List of audio data frames

        Returns:
            Path to the saved file
        """
        try:
            with wave.Wave_write(self.output_file) as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(b"".join(frames))

            return self.output_file
        except Exception as err:
            raise IOError(f"Failed to save recording: {err}") from err


def main() -> None:
    """Execute the voice recorder as a standalone application."""
    recorder = VoiceRecorder()
    recorder.record_until_silence()


if __name__ == "__main__":
    main()
