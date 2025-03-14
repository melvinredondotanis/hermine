"""
Module for text-to-speech conversion using OpenAI's API.
"""
from pathlib import Path
from typing import Optional, Union


from openai import OpenAI


class TextToSpeechConverter:
    """A class for converting text to speech using OpenAI's API."""

    def __init__(
        self,
        model: str = "tts-1-hd",
        voice: str = "sage",
        api_key: Optional[str] = None
    ) -> None:
        """
        Initialize the TTS converter.

        Args:
            model: The TTS model to use
            voice: The voice type for speech synthesis
            api_key: Optional API key (uses environment variable if not provided)
        """
        self.model = model
        self.voice = voice
        self.client = OpenAI(api_key=api_key)

    def generate_speech(
        self,
        text: str,
        output_path: Union[str, Path]
    ) -> Path:
        """
        Convert text to speech and save to file.

        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file

        Returns:
            Path object pointing to the saved file

        Raises:
            ValueError: If text is empty
            RuntimeError: If speech generation or file saving fails
        """
        if not text:
            raise ValueError("Input text cannot be empty")

        # Ensure output_path is a Path object
        if isinstance(output_path, str):
            output_path = Path(output_path)

        # Create parent directories if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with self.client.audio.speech.with_streaming_response.create(
                model=self.model,
                voice=self.voice,
                input=text,
            ) as response:
                response.stream_to_file(str(output_path))
            return output_path
        except Exception as e:
            raise RuntimeError(f"Speech generation error: {str(e)}") from e

    def update_settings(self, model: Optional[str] = None, voice: Optional[str] = None) -> None:
        """
        Update TTS model and voice settings.

        Args:
            model: New model to use
            voice: New voice to use
        """
        if model:
            self.model = model
        if voice:
            self.voice = voice


def main() -> None:
    """Run the TTS converter with default settings."""
    speech_file_path = Path(__file__).parent / "speech.mp3"
    converter = TextToSpeechConverter()
    converter.generate_speech(
        "Today is a wonderful day to build something people love!",
        speech_file_path
    )


if __name__ == "__main__":
    main()
