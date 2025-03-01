import sys
import argparse

from ollama import chat
from rich.console import Console


global messages
messages = []


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Your copilot for Linux'
        )
    return parser.parse_args()


def main():
    """Main function of the application."""
    global messages
    args = parse_arguments()
    console = Console()

    try:
        while True:
            try:
                console.print(
                    ">>> ",
                    end="",
                    style="bold green"
                )
                user_input = input()
                if user_input.lower() in ['!exit', '!quit']:
                    break
                elif user_input.lower() == '!help':
                    print("Available commands:")
                    print("    !exit, !quit     Exit the application")
                    print("    !help            Show this help message")

            except KeyboardInterrupt:
                print("\nUser interrupted.")
                break
            except EOFError:
                print("\nUser interrupted.")
                break

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
            console.print(
                response.message.content,
                style="bold blue"
            )
        return 0

    except KeyboardInterrupt:
        print("\nUser interrupted.")
        return 1
    except EOFError:
        print("\nUser interrupted.")
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
