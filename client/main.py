"""Main module of the application."""

import sys
import argparse
import requests

from ollama import chat
from rich.console import Console
from rich.markdown import Markdown


VERSION = "0.0.0"
HOST = "http://localhost:5000"

global messages
messages = []


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Your copilot for Linux'
        )
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=VERSION
        )
    return parser.parse_args()


def main():
    """Main function of the application."""
    global messages
    args = parse_arguments()
    console = Console()

    try:
        current_chat = requests.post(f"{HOST}/history/chat").json().get("chat_id")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        while True:
            try:
                console.print(
                    f">>> ",
                    end="",
                    style="bold blue"
                )
                user_input = input()
                if user_input.lower() in ['!exit', '!quit']:
                    break
                elif user_input.lower() == '!help':
                    print("Available commands:")
                    print("    !exit, !quit     Exit the application")
                    print("    !clear           Clear the chat")
                    print("    !version         Show the version")
                    print("    !help            Show this help message")
                    continue
                elif user_input.lower() == '!version':
                    print(VERSION)
                    continue
                elif user_input.lower() == '!clear':
                    messages = []
                    continue
                elif user_input == "":
                    continue
                elif user_input.startswith("!"):
                    console.print(
                        "Unknown command. Type !help for help.",
                        style="bold red"
                        )
                    continue             
            except KeyboardInterrupt:
                console.print(
                    "Goodbye!",
                    style="bold green"
                    )
                break
            except EOFError:
                console.print(
                    "Goodbye!",
                    style="bold green"
                    )
                break


            with console.status("[bold green]Thinking..."):
                response = chat(
                    model="hermine",
                    messages=messages+[
                        {
                            "role": "user",
                            "content": user_input
                        }
                    ]
                )
                messages += [
                    {
                        "role": "user",
                        "content": user_input
                    },
                    {
                        "role": "assistant",
                        "content": response.message.content
                    }
                ]
            output = Markdown(response.message.content)
            console.print(
                output,
                style="bold white"
            )
        return 0

    except KeyboardInterrupt:
        console.print(
            "Goodbye!",
            style="bold green"
            )
        return 1
    except EOFError:
        console.print(
            "Goodbye!",
            style="bold green"
            )
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
