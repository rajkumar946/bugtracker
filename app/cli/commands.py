import asyncio
import typer
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
import getpass

from app.db.session import get_db
from app.models.user import User, RoleEnum
from app.core.security import hash_password

app = typer.Typer(help="User management commands")
console = Console()

@app.command("create")
def create_user_cmd(
    email: str = typer.Option(..., "--email", "-e", help="User email address"),
    full_name: Optional[str] = typer.Option(None, "--name", "-n", help="User full name"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="User password (will prompt if not provided)"),
    verified: bool = typer.Option(False, "--verified", "-v", help="Mark user as verified"),
    role: str = typer.Option("user", "--role", "-r", help="User role (admin, developer, qa, project_manager, user)"),
    interactive: bool = typer.Option(True, "--interactive/--non-interactive", "-i", help="Interactive mode")
):
    """Create a new user"""
    asyncio.run(_create_user_async(email, full_name, password, verified, role, interactive))

async def _create_user_async(
    email: str, 
    full_name: Optional[str], 
    password: Optional[str], 
    verified: bool, 
    role: str, 
    interactive: bool
):
    """Async function to create user"""
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    try:
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == email))
        existing_user = result.scalars().first()
        
        if existing_user:
            console.print(f"[red]Error: User with email {email} already exists![/red]")
            raise typer.Exit(1)
        
        # Interactive mode for missing information
        if interactive:
            if not full_name:
                full_name = Prompt.ask("Enter full name", default="")
            
            if not password:
                password = getpass.getpass("Enter password: ")
                confirm_password = getpass.getpass("Confirm password: ")
                
                if password != confirm_password:
                    console.print("[red]Error: Passwords don't match![/red]")
                    raise typer.Exit(1)
            
            if not verified:
                verified = Confirm.ask("Mark user as verified?")
            
            # Role selection
            available_roles = [role.value for role in RoleEnum]
            console.print(f"Available roles: {', '.join(available_roles)}")
            role = Prompt.ask("Select role", default="user", choices=available_roles)
        
        if not password:
            console.print("[red]Error: Password is required![/red]")
            raise typer.Exit(1)
        
        # Validate role
        try:
            role_enum = RoleEnum(role)
        except ValueError:
            available_roles = [r.value for r in RoleEnum]
            console.print(f"[red]Error: Invalid role '{role}'. Available roles: {', '.join(available_roles)}[/red]")
            raise typer.Exit(1)
        
        # Create user directly in database
        user = User(
            email=email,
            full_name=full_name or "",
            hashed_password=hash_password(password),
            is_verified=verified,
            role=role_enum,
            verification_token=None if verified else None
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Display success message
        panel = Panel.fit(
            f"✅ User created successfully!\n\n"
            f"ID: {user.id}\n"
            f"Email: {user.email}\n"
            f"Name: {user.full_name or 'Not provided'}\n"
            f"Role: {user.role.value}\n"
            f"Verified: {'Yes' if user.is_verified else 'No'}\n"
            f"Admin: {'Yes' if user.is_superuser else 'No'}",
            title="User Created",
            border_style="green"
        )
        console.print(panel)
        
    except Exception as e:
        await db.rollback()
        console.print(f"[red]Error creating user: {str(e)}[/red]")
        raise typer.Exit(1)
    finally:
        # Properly close the generator
        try:
            await db_gen.__anext__()
        except StopAsyncIteration:
            pass

@app.command("list")
def list_users(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of users to display"),
    offset: int = typer.Option(0, "--offset", "-o", help="Number of users to skip"),
    verified_only: bool = typer.Option(False, "--verified-only", help="Show only verified users"),
    role: Optional[str] = typer.Option(None, "--role", help="Filter by role (admin, developer, qa, project_manager, user)")
):
    """List users"""
    asyncio.run(_list_users_async(limit, offset, verified_only, role))

async def _list_users_async(limit: int, offset: int, verified_only: bool, role: Optional[str]):
    """Async function to list users"""
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    try:
        query = select(User)
        
        if verified_only:
            query = query.where(User.is_verified == True)
        
        if role:
            try:
                role_enum = RoleEnum(role)
                query = query.where(User.role == role_enum)
            except ValueError:
                available_roles = [r.value for r in RoleEnum]
                console.print(f"[red]Error: Invalid role '{role}'. Available roles: {', '.join(available_roles)}[/red]")
                raise typer.Exit(1)
        
        query = query.offset(offset).limit(limit)
        result = await db.execute(query)
        users = result.scalars().all()
        
        if not users:
            console.print("[yellow]No users found![/yellow]")
            return
        
        table = Table(title="Users")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Email", style="magenta")
        table.add_column("Name", style="green")
        table.add_column("Role", style="blue")
        table.add_column("Verified", style="yellow")
        table.add_column("Active", style="red")
        table.add_column("Created", style="dim")
        
        for user in users:
            # Role emoji mapping
            role_emoji = {
                "admin": "👑",
                "developer": "💻",
                "qa": "🧪",
                "project_manager": "📋",
                "user": "👤"
            }
            
            table.add_row(
                str(user.id),
                user.email,
                user.full_name or "N/A",
                f"{role_emoji.get(user.role.value, '👤')} {user.role.value}",
                "✅" if user.is_verified else "❌",
                "✅" if user.is_active else "❌",
                user.created_at.strftime("%Y-%m-%d %H:%M")
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing users: {str(e)}[/red]")
        raise typer.Exit(1)
    finally:
        # Properly close the generator
        try:
            await db_gen.__anext__()
        except StopAsyncIteration:
            pass

@app.command("delete")
def delete_user_cmd(
    email: str = typer.Option(..., "--email", "-e", help="User email to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt")
):
    """Delete a user"""
    asyncio.run(_delete_user_async(email, force))

async def _delete_user_async(email: str, force: bool):
    """Async function to delete user"""
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    try:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        
        if not user:
            console.print(f"[red]Error: User with email {email} not found![/red]")
            raise typer.Exit(1)
        
        if not force:
            confirm = Confirm.ask(f"Are you sure you want to delete user {email}?")
            if not confirm:
                console.print("[yellow]Operation cancelled.[/yellow]")
                return
        
        await db.delete(user)
        await db.commit()
        
        console.print(f"[green]✅ User {email} deleted successfully![/green]")
        
    except Exception as e:
        await db.rollback()
        console.print(f"[red]Error deleting user: {str(e)}[/red]")
        raise typer.Exit(1)
    finally:
        # Properly close the generator
        try:
            await db_gen.__anext__()
        except StopAsyncIteration:
            pass

@app.command("verify")
def verify_user_cmd(
    email: str = typer.Option(..., "--email", "-e", help="User email to verify")
):
    """Verify a user's email"""
    asyncio.run(_verify_user_async(email))

async def _verify_user_async(email: str):
    """Async function to verify user"""
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    try:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        
        if not user:
            console.print(f"[red]Error: User with email {email} not found![/red]")
            raise typer.Exit(1)
        
        if user.is_verified:
            console.print(f"[yellow]User {email} is already verified![/yellow]")
            return
        
        user.is_verified = True
        user.verification_token = None
        await db.commit()
        
        console.print(f"[green]✅ User {email} verified successfully![/green]")
        
    except Exception as e:
        await db.rollback()
        console.print(f"[red]Error verifying user: {str(e)}[/red]")
        raise typer.Exit(1)
    finally:
        # Properly close the generator
        try:
            await db_gen.__anext__()
        except StopAsyncIteration:
            pass

@app.command("change-password")
def change_password_cmd(
    email: str = typer.Option(..., "--email", "-e", help="User email"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="New password (will prompt if not provided)")
):
    """Change user password"""
    asyncio.run(_change_password_async(email, password))

async def _change_password_async(email: str, password: Optional[str]):
    """Async function to change user password"""
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    try:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        
        if not user:
            console.print(f"[red]Error: User with email {email} not found![/red]")
            raise typer.Exit(1)
        
        if not password:
            password = getpass.getpass("Enter new password: ")
            confirm_password = getpass.getpass("Confirm new password: ")
            
            if password != confirm_password:
                console.print("[red]Error: Passwords don't match![/red]")
                raise typer.Exit(1)
        
        user.hashed_password = hash_password(password)
        user.reset_token = None  # Clear any existing reset tokens
        await db.commit()
        
        console.print(f"[green]✅ Password changed successfully for {email}![/green]")
        
    except Exception as e:
        await db.rollback()
        console.print(f"[red]Error changing password: {str(e)}[/red]")
        raise typer.Exit(1)
    finally:
        # Properly close the generator
        try:
            await db_gen.__anext__()
        except StopAsyncIteration:
            pass

@app.command("update-role")
def update_role_cmd(
    email: str = typer.Option(..., "--email", "-e", help="User email"),
    role: str = typer.Option(..., "--role", "-r", help="New role (admin, developer, qa, project_manager, user)")
):
    """Update user role"""
    asyncio.run(_update_role_async(email, role))

async def _update_role_async(email: str, role: str):
    """Async function to update user role"""
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    try:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        
        if not user:
            console.print(f"[red]Error: User with email {email} not found![/red]")
            raise typer.Exit(1)
        
        # Validate role
        try:
            role_enum = RoleEnum(role)
        except ValueError:
            available_roles = [r.value for r in RoleEnum]
            console.print(f"[red]Error: Invalid role '{role}'. Available roles: {', '.join(available_roles)}[/red]")
            raise typer.Exit(1)
        
        old_role = user.role.value
        user.role = role_enum
        await db.commit()
        
        console.print(f"[green]✅ User {email} role updated from '{old_role}' to '{role}'![/green]")
        
    except Exception as e:
        await db.rollback()
        console.print(f"[red]Error updating user role: {str(e)}[/red]")
        raise typer.Exit(1)
    finally:
        # Properly close the generator
        try:
            await db_gen.__anext__()
        except StopAsyncIteration:
            pass

if __name__ == "__main__":
    app()