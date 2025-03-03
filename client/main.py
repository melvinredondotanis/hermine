"""Main module of the application."""

import re
import os
import sys
import argparse
import requests

from ollama import chat
from rich.console import Console
from rich.markdown import Markdown
import subprocess


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
    parser.add_argument(
        '-p',
        '--prompt',
        type=str,
        help='The prompt to use for the chat'
    )
    return parser.parse_args()


def main():
    """Main function of the application."""
    global messages
    args = parse_arguments()
    console = Console()
    last_sugessted_command = None

    if args.prompt:
        current_path = os.getcwd()
        try:
            ls_output = subprocess.check_output(['ls', '-la', current_path], text=True)
            context = f"Current directory: {current_path}\n\nDirectory listing:\n{ls_output}"
        except Exception as e:
            context = f"Error getting directory listing: {str(e)}"

        messages = [
            {
            "role": "user",
            "content": f"{args.prompt}\n\nRequirements: Responds to my request as well as possible with just one and the same bash command with all the actions. Context: {context}"
            }
        ]
        response = chat(
            model="hermine",
            messages=messages
        )
        messages += [
            {
                "role": "assistant",
                "content": response.message.content
            }
        ]
        print(response.message.content)
        code_blocks = re.findall(r'```(?:\w+)?\s*\n(.*?)\n```', response.message.content, re.DOTALL)
        last_sugessted_command = code_blocks[0].strip() if code_blocks else None
        print(last_sugessted_command)
        if last_sugessted_command:
            run = subprocess.run(last_sugessted_command, shell=True, capture_output=True, text=True)
            print(run.stdout)
        else:
            print("No command was found in the response.")
        output = Markdown(response.message.content)
        console.print(
            output,
            style="bold white"
            )
        return 0

    try:
        response = requests.post(f"{HOST}/history/chat")
        json_response = response.json()
        if isinstance(json_response, dict):
            current_chat = json_response.get("chat_id")
        else:
            print(f"Error: Expected dictionary response, got {type(json_response).__name__}", file=sys.stderr)
            return 1
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        current_container = requests.get(f"{HOST}/history/chat/{current_chat}").json().get("container_id")
        if not current_container:
            current_container = requests.get(f"{HOST}/sandbox/create/debian").json().get("container_id")
            requests.post(f"{HOST}/history/chat/{current_chat}/container", json={"container_id": current_container})
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
                    print("    !try             Try the suggested command in a container")
                    print("    !run             Run a command in the current container")
                    print("    !apply           Apply the suggested command to your system")
                    print("    !version         Show the version")
                    print("    !help            Show this help message")
                    continue
                elif user_input.lower() == '!version':
                    print(VERSION)
                    continue
                elif user_input.lower() == '!clear':
                    messages = []
                    continue
                elif user_input.lower() == '!try':
                    if last_sugessted_command:
                        try:
                            with console.status("[bold green]Starting container..."):
                                response = requests.get(
                                    f"{HOST}/sandbox/start/{current_container}"
                                )
                                if not response.json().get("success"):
                                    print("Error: Failed to start container", file=sys.stderr)
                                    continue       
                            with console.status("[bold green]Executing..."):                                
                                response = requests.post(
                                    f"{HOST}/sandbox/execute/{current_container}",
                                    json={"command": last_sugessted_command},
                                    stream=True
                                    )
                                if response.status_code == 200:
                                    console.print(
                                        f"@container:{current_container}\n$ {last_sugessted_command}",
                                        style="yellow"
                                    )
                                    for line in response.iter_lines():
                                        if line:
                                            console.print(
                                                line.decode("utf-8"),
                                                style="green"
                                            )
                                else:
                                    print(f"Error: {response.json().get('error')}", file=sys.stderr)
                        except requests.exceptions.RequestException as e:
                            print(f"Error: {e}", file=sys.stderr)
                    else:
                        console.print(
                            "No suggested command to try.",
                            style="bold red"
                        )
                    continue
                elif user_input.lower() == '!run':
                    try:
                        console.print(
                            f"@container:{current_container}",
                            style="yellow"
                        )
                        console.print(
                            f"$ ",
                            end="",
                            style="yellow"
                        )
                        user_input = input()
                        with console.status("[bold green]Executing..."):
                            response = requests.post(
                                f"{HOST}/sandbox/execute/{current_container}",
                                json={"command": user_input},
                                stream=True
                                )
                            if response.status_code == 200:
                                for line in response.iter_lines():
                                    if line:
                                        console.print(
                                            line.decode("utf-8"),
                                            style="green"
                                        )
                            else:
                                print(f"Error: {response.json().get('error')}", file=sys.stderr)
                    except requests.exceptions.RequestException as e:
                        print(f"Error: {e}", file=sys.stderr)
                    continue
                elif user_input.lower() == '!apply':
                    if last_sugessted_command:
                        try:
                            with console.status("[bold green]Executing..."):
                                response = requests.post(
                                    f"{HOST}/system/execute",
                                    json={"command": last_sugessted_command}
                                )
                                if response.status_code == 200:
                                    console.print(
                                        response.json().get("output"),
                                        style="green"
                                    )
                                else:
                                    print(f"Error: {response.json().get('error')}", file=sys.stderr)
                        except requests.exceptions.RequestException as e:
                            print(f"Error: {e}", file=sys.stderr)
                    else:
                        console.print(
                            "No suggested command to apply.",
                            style="bold red"
                        )
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
                    "\nGoodbye!",
                    style="bold green"
                    )
                break
            except EOFError:
                console.print(
                    "\nGoodbye!",
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
            code_blocks = re.findall(r'```(?:\w+)?\s*\n(.*?)\n```', response.message.content, re.DOTALL)
            last_sugessted_command = code_blocks[0].strip() if code_blocks else None
            output = Markdown(response.message.content)
            console.print(
                output,
                style="bold white"
            )
        return 0

    except KeyboardInterrupt:
        console.print(
            "\nGoodbye!",
            style="bold green"
            )
        return 1
    except EOFError:
        console.print(
            "\nGoodbye!",
            style="bold green"
            )
        return 1
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
