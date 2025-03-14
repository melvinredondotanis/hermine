"""
Text Generator Module using OpenAI API.
"""
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import openai
from openai import OpenAI
from openai.types.chat import ChatCompletion


@dataclass
class Message:
    """Represents a message in a chat conversation."""

    role: str
    content: str

    def to_dict(self) -> Dict[str, str]:
        """Convert the message to a dictionary format for OpenAI API."""
        return {"role": self.role, "content": self.content}


class TextGenerator:
    """Class for generating text using OpenAI's API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """Initialize the TextGenerator with OpenAI client.

        Args:
            api_key: OpenAI API key. Defaults to environment variable.
            model: The model to use for text generation.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def generate(self, messages: List[Message], **kwargs) -> Optional[str]:
        """Generate text based on the provided messages.

        Args:
            messages: List of messages for context generation.
            **kwargs: Additional parameters to pass to the OpenAI API.

        Returns:
            The generated text or None if an error occurred.
        """
        try:
            formatted_messages = [message.to_dict() for message in messages]

            completion: ChatCompletion = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                **kwargs
            )

            if completion.choices:
                return completion.choices[0].message.content
            return None
        except (
            openai.APIError,
            openai.APIConnectionError,
            openai.RateLimitError,
            openai.AuthenticationError,
            ValueError
            ) as error:
            print(f"Error generating text: {error}")
            return None

    def get_model(self) -> str:
        """Get the current model being used.
        
        Returns:
            The name of the current model.
        """
        return self.model


def main() -> None:
    """Execute the main program logic."""
    generator = TextGenerator()

    messages = [
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="Write a haiku about recursion in programming.")
    ]

    response = generator.generate(messages)

    if response:
        print(f"Generated text:\n{response}")
    else:
        print("Failed to generate text. Check logs for details.")


if __name__ == "__main__":
    main()
