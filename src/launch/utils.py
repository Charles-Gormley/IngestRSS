import os
from typing import List, Dict, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
import random
import boto3

console = Console()

def animate_text(text: str, emoji_list: List[str], duration: float = 0.05):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description="", total=len(text))
        for char in text:
            time.sleep(duration)
            emoji = random.choice(emoji_list)
            progress.update(task, advance=1, description=f"{emoji} {text[:progress.tasks[0].completed + 1]}")
    console.print()

def create_dropdown(options: List[str], prompt: str) -> str:
    table = Table(show_header=False, box=None)
    for i, option in enumerate(options, 1):
        table.add_row(f"{i}. {option}")
    console.print(table)
    return Prompt.ask(prompt, choices=[str(i) for i in range(1, len(options) + 1)])

def get_env_value(key: str, prompt: str, options: List[str] = None, advanced: bool = False) -> str:
    if advanced and not Confirm.ask("Do you want to configure advanced settings?"):
        return os.environ.get(key, "")
    
    if options:
        choice = create_dropdown(options, prompt)
        return options[int(choice) - 1]
    else:
        return Prompt.ask(prompt)

def display_summary(env_vars: Dict[str, Any]):
    table = Table(title="Environment Variables Summary")
    table.add_column("Variable", style="cyan")
    table.add_column("Value", style="magenta")
    
    for key, value in env_vars.items():
        if key in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]:
            value = "********" if value else ""
        table.add_row(key, str(value))
    
    console.print(table)

def save_env_file(env_vars: Dict[str, Any]):
    with open(".env", "w") as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    console.print(Panel(Text("Environment variables saved to .env file", style="bold green")))

def get_aws_regions() -> List[str]:
    try:
        ec2_client = boto3.client('ec2')
        regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
        return sorted(regions)
    except Exception as e:
        console.print(f"[bold red]Error fetching AWS regions: {str(e)}[/bold red]")
        console.print("[yellow]Falling back to default region list.[/yellow]")
        return ["us-east-1", "us-east-2", "us-west-1", "us-west-2", "eu-west-1", "eu-central-1", "ap-southeast-1", "ap-southeast-2"]

emojis = ["🦍", "🗞️", "💵", "🚀", "☕", "🌻", "☀️", "🌴", "🌳", "🌲", "🎋"]