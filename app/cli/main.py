# app/cli/main.py
import typer
from app.cli.commands import app as user_commands

app = typer.Typer(help="FastAPI Application CLI")

# Add user management commands
app.add_typer(user_commands, name="user", help="User management commands")

if __name__ == "__main__":
    app()