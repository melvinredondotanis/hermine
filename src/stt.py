"""
Speech-to-text module using OpenAI's Whisper model.
"""
from typing import Optional
from pathlib import Path

from openai import OpenAI


class AudioTranscriber: # pylint: disable=too-few-public-methods
    """A class to handle audio transcription using OpenAI's API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "whisper-1"):
        """
        Initialize the AudioTranscriber.

        Args:
            api_key: OpenAI API key. If None, uses OPENAI_API_KEY environment variable.
            model: The transcription model to use.
        """
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key)

    def transcribe_file(self, file_path: str) -> str:
        """
        Transcribe an audio file to text.

        Args:
            file_path: Path to the audio file.

        Returns:
            Transcription text.

        Raises:
            FileNotFoundError: If the audio file doesn't exist.
            ValueError: For API or processing errors.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        try:
            with open(file_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    response_format="text"
                )
                return transcription
        except Exception as e:
            raise ValueError(f"Transcription error: {str(e)}") from e


def main() -> None:
    """Main function to demonstrate the AudioTranscriber class."""
    try:
        transcriber = AudioTranscriber()
        result = transcriber.transcribe_file("hermine_recording.wav")
        print(result)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
