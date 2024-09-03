import os
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.text import Text
from time import sleep

console = Console()

def animate_text(text):
    for char in text:
        console.print(char, end='', style="bold green")
        sleep(0.05)
    print()

def set_env_var(name, value):
    os.environ[name] = value
    animate_text(f"Environment variable {name} set to {value}")

def list_env_vars():
    animate_text("Current environment variables:")
    for key, value in os.environ.items():
        console.print(f"{key}: {value}")

def main():
    while True:
        action = prompt(
            "Choose an action (set/list/quit): ",
            completer=WordCompleter(['set', 'list', 'quit'])
        )

        if action == 'set':
            name = prompt("Enter variable name: ")
            value = prompt("Enter variable value: ")
            set_env_var(name, value)
        elif action == 'list':
            list_env_vars()
        elif action == 'quit':
            animate_text("Goodbye!")
            break
        else:
            console.print("Invalid action. Please try again.", style="bold red")

if __name__ == "__main__":
    main()