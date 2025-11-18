# cli/commands/config.py (extrait pour config)

import typer
from rich.console import Console
from rich.table import Table

from gformfiller.infrastructure.config import (
    ConfigLoader,
    ConfigPaths,
    ConfigInitializer,
    ConfigValidator,
)
import sys

config_app = typer.Typer(help="Configuration management commands")
console = Console()

@config_app.command("init")
def init_config(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing configuration")
):
    """Initialize configuration structure"""
    if ConfigPaths.exists() and not force:
        console.print("[yellow]Configuration already exists. Use --force to reinitialize.[/yellow]")
        return
    
    success = ConfigInitializer.initialize(force=force)
    
    if success:
        print(f"[green]✓[/green] Configuration initialized at {ConfigPaths.BASE_DIR}")
        print(f"\nCreated structure:")
        print(f"  • {ConfigPaths.CONFIG_DIR}")
        print(f"  • {ConfigPaths.PARSERS_DIR}")
        print(f"  • {ConfigPaths.RESPONSES_DIR}")
        print(f"  • {ConfigPaths.PROMPTS_DIR}")
        print(f"  • {ConfigPaths.LOGS_DIR}")
        print(f"  • {ConfigPaths.CACHE_DIR}")
    else:
        console.print("[red]✗[/red] Initialization failed")


@config_app.command("show")
def show_config(
    source: bool = typer.Option(False, "--source", "-s", help="Show source of each value"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, json, toml"),
):
    """Display current configuration"""
    try:
        config = ConfigLoader.load()
        
        if format == "json":
            import json
            # Use standard print to avoid Rich formatting
            output = json.dumps(config.model_dump(), indent=2, default=str)
            console.print(output)
        elif format == "toml":
            import tomli_w
            # model_dump() preserves nested structure
            config_dict = config.model_dump()
            toml_str = tomli_w.dumps(config_dict)
            console.print(toml_str)
        else:  # table
            _display_config_table(config, show_source=source)
            
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        raise typer.Exit(1)


def _display_config_table(config, show_source: bool = False):
    """Display configuration as rich table"""
    
    # Timeouts section
    table = Table(title="⏱️  Timeouts", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    if show_source:
        table.add_column("Source", style="yellow")
    
    table.add_row("Page Load", f"{config.timeouts.page_load}s")
    table.add_row("Element Wait", f"{config.timeouts.element_wait}s")
    table.add_row("Script Execution", f"{config.timeouts.script_execution}s")
    table.add_row("AI Response", f"{config.timeouts.ai_response}s")
    table.add_row("Form Submission", f"{config.timeouts.form_submission}s")
    console.print(table)
    console.print()
    
    # Retry section
    table = Table(title="🔄 Retry", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Max Attempts", str(config.retry.max_attempts))
    table.add_row("Backoff Factor", f"{config.retry.backoff_factor}x")
    table.add_row("Initial Delay", f"{config.retry.initial_delay}s")
    console.print(table)
    console.print()
    
    # Browser section
    table = Table(title="🌐 Browser", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Window Size", f"{config.browser.window_width}x{config.browser.window_height}")
    table.add_row("Page Load Strategy", config.browser.page_load_strategy)
    table.add_row("User Agent", config.browser.user_agent or "(default)")
    console.print(table)
    console.print()
    
    # AI section
    table = Table(title="🤖 AI", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Default Provider", config.ai.default_provider)
    table.add_row("Max Tokens", str(config.ai.max_tokens))
    table.add_row("Temperature", str(config.ai.temperature))
    table.add_row("Stream Timeout", f"{config.ai.stream_timeout}s")
    console.print(table)
    console.print()
    
    # Logging section
    table = Table(title="📝 Logging", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Level", config.logging.level)
    table.add_row("Format", config.logging.format)
    table.add_row("Max File Size", f"{config.logging.max_file_size_mb} MB")
    table.add_row("Backup Count", str(config.logging.backup_count))
    console.print(table)
    console.print()


@config_app.command("paths")
def show_paths():
    """Display configuration file paths"""
    table = Table(title="📁 Configuration Paths", show_header=True)
    table.add_column("Location", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Exists", style="yellow")
    
    paths_to_show = [
        ("Base Directory", ConfigPaths.BASE_DIR),
        ("Config Directory", ConfigPaths.CONFIG_DIR),
        ("Constants File", ConfigPaths.CONSTANTS_FILE),
        ("Logging File", ConfigPaths.LOGGING_FILE),
        ("Parsers Directory", ConfigPaths.PARSERS_DIR),
        ("Responses Directory", ConfigPaths.RESPONSES_DIR),
        ("Prompts Directory", ConfigPaths.PROMPTS_DIR),
        ("Logs Directory", ConfigPaths.LOGS_DIR),
        ("Cache Directory", ConfigPaths.CACHE_DIR),
        ("Default Prompt", ConfigPaths.DEFAULT_PROMPT_FILE),
    ]
    
    for name, path in paths_to_show:
        exists = "✓" if path.exists() else "✗"
        exists_style = "green" if path.exists() else "red"
        table.add_row(name, str(path), f"[{exists_style}]{exists}[/{exists_style}]")
    
    console.print(table)


@config_app.command("validate")
def validate_config():
    """Validate configuration files"""
    console.print("[bold]Validating configuration...[/bold]\n")
    
    all_valid = True
    
    # Validate config file
    console.print("📋 Checking constants.toml...")
    is_valid, errors = ConfigValidator.validate_config_file()
    if is_valid:
        console.print("[green]  ✓ Valid[/green]")
    else:
        console.print("[red]  ✗ Invalid[/red]")
        for error in errors:
            console.print(f"    • {error}")
        all_valid = False
    
    console.print()
    
    # Validate paths
    console.print("📁 Checking directory structure...")
    paths_valid, missing = ConfigValidator.validate_paths()
    if paths_valid:
        console.print("[green]  ✓ All paths exist[/green]")
    else:
        console.print("[yellow]  ⚠ Missing paths:[/yellow]")
        for path in missing:
            console.print(f"    • {path}")
        all_valid = False
    
    console.print()
    
    # Check API keys
    console.print("🔑 Checking API keys...")
    from gformfiller.infrastructure.config.defaults import SUPPORTED_AI_PROVIDERS
    
    for provider in SUPPORTED_AI_PROVIDERS:
        has_key, _ = ConfigValidator.check_api_keys(provider)
        status = "[green]✓[/green]" if has_key else "[red]✗[/red]"
        console.print(f"  {status} {provider}")
    
    console.print()
    
    if all_valid:
        console.print("[bold green]✓ Configuration is valid[/bold green]")
    else:
        console.print("[bold yellow]⚠ Configuration has warnings[/bold yellow]")
        raise typer.Exit(1)


@config_app.command("edit")
def edit_config(
    file: str = typer.Option("constants", "--file", "-f", help="File to edit: constants, logging")
):
    """Open configuration file in default editor"""
    import subprocess
    import sys
    
    file_map = {
        "constants": ConfigPaths.CONSTANTS_FILE,
        "logging": ConfigPaths.LOGGING_FILE,
    }
    
    if file not in file_map:
        console.print(f"[red]Unknown file: {file}. Choose: constants, logging[/red]")
        raise typer.Exit(1)
    
    file_path = file_map[file]
    
    if not file_path.exists():
        console.print(f"[red]File not found: {file_path}[/red]")
        console.print("Run 'gformfiller config init' first")
        raise typer.Exit(1)
    
    # Get editor from environment or use default
    import os
    editor = os.getenv("EDITOR", "nano" if sys.platform != "win32" else "notepad")
    
    try:
        subprocess.run([editor, str(file_path)], check=True)
        console.print(f"[green]✓[/green] File edited: {file_path}")
    except subprocess.CalledProcessError:
        console.print(f"[red]Failed to open editor: {editor}[/red]")
        raise typer.Exit(1)


@config_app.command("set")
def set_config_value(
    key: str = typer.Argument(..., help="Configuration key (e.g., timeouts.page_load)"),
    value: str = typer.Argument(..., help="New value"),
):
    """Set a configuration value"""
    try:
        # Load current config
        import tomli
        with open(ConfigPaths.CONSTANTS_FILE, "rb") as f:
            config_dict = tomli.load(f)
        
        # Parse key path
        keys = key.split(".")
        
        # Navigate to the nested key
        current = config_dict
        for k in keys[:-1]:
            if k not in current:
                console.print(f"[red]Key not found: {k}[/red]")
                raise typer.Exit(1)
            current = current[k]
        
        # Parse value
        parsed_value = _parse_value(value)
        
        # Set value
        final_key = keys[-1]
        if final_key not in current:
            console.print(f"[red]Key not found: {final_key}[/red]")
            raise typer.Exit(1)
        
        old_value = current[final_key]
        current[final_key] = parsed_value
        
        # Update last_modified timestamp
        from datetime import datetime
        config_dict["meta"]["last_modified"] = datetime.now().isoformat()
        
        # Validate new config
        try:
            from gformfiller.infrastructure.config import ConstantsConfig
            ConstantsConfig(**config_dict)
        except Exception as e:
            console.print(f"[red]Invalid value: {e}[/red]")
            raise typer.Exit(1)
        
        # Write back to file
        import tomli_w
        with open(ConfigPaths.CONSTANTS_FILE, "wb") as f:
            tomli_w.dump(config_dict, f)
        
        console.print(f"[green]✓[/green] Updated {key}: {old_value} → {parsed_value}")
        
    except Exception as e:
        console.print(f"[red]Error setting value: {e}[/red]")
        raise typer.Exit(1)


def _parse_value(value: str):
    """Parse string value to appropriate type"""
    # Boolean
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    
    # Integer
    try:
        return int(value)
    except ValueError:
        pass
    
    # Float
    try:
        return float(value)
    except ValueError:
        pass
    
    # String
    return value


@config_app.command("clean-logs")
def clean_logs(
    older_than_days: int = typer.Option(7, "--older-than", "-o", help="Delete logs older than N days"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Show what would be deleted"),
):
    """Clean old log files"""
    from datetime import datetime, timedelta
    import time
    
    cutoff_date = datetime.now() - timedelta(days=older_than_days)
    deleted_count = 0
    deleted_size = 0
    
    console.print(f"🗑️  Cleaning logs older than {older_than_days} days...")
    console.print()
    
    for log_file in ConfigPaths.LOGS_DIR.glob("*.log*"):
        if log_file.name == ".gitkeep":
            continue
        
        file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        
        if file_mtime < cutoff_date:
            file_size = log_file.stat().st_size
            
            if dry_run:
                console.print(f"  Would delete: {log_file.name} ({file_size} bytes)")
            else:
                log_file.unlink()
                console.print(f"  Deleted: {log_file.name} ({file_size} bytes)")
            
            deleted_count += 1
            deleted_size += file_size
    
    console.print()
    if deleted_count > 0:
        size_mb = deleted_size / (1024 * 1024)
        action = "Would delete" if dry_run else "Deleted"
        console.print(f"[green]{action} {deleted_count} log file(s) ({size_mb:.2f} MB)[/green]")
    else:
        console.print("[yellow]No old log files found[/yellow]")


@config_app.command("clean-cache")
def clean_cache(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Clean cache directory"""
    import shutil
    
    if not confirm:
        confirm = typer.confirm("Are you sure you want to delete all cached data?")
    
    if not confirm:
        console.print("Cancelled")
        return
    
    try:
        # Remove all files in cache dir
        for item in ConfigPaths.CACHE_DIR.iterdir():
            if item.name == ".gitkeep":
                continue
            
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        
        console.print(f"[green]✓[/green] Cache cleaned: {ConfigPaths.CACHE_DIR}")
    except Exception as e:
        console.print(f"[red]Error cleaning cache: {e}[/red]")
        raise typer.Exit(1)


@config_app.command("reset")
def reset_config(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Reset configuration to defaults (DANGEROUS)"""
    if not confirm:
        console.print("[bold red]⚠️  WARNING: This will delete all your configuration![/bold red]")
        console.print("This includes:")
        console.print("  • Configuration files")
        console.print("  • Parsers")
        console.print("  • Responses")
        console.print("  • Custom prompts")
        console.print("  • Logs")
        console.print("  • Cache")
        console.print()
        confirm = typer.confirm("Are you ABSOLUTELY sure?")
    
    if not confirm:
        console.print("Cancelled")
        return
    
    try:
        import shutil
        import time

        # Backup current config
        backup_path = ConfigPaths.BASE_DIR.parent / f".gformfiller_backup_{int(time.time())}"
        shutil.copytree(ConfigPaths.BASE_DIR, backup_path)
        console.print(f"[yellow]Backup created: {backup_path}[/yellow]")
        
        # Remove and reinitialize
        shutil.rmtree(ConfigPaths.BASE_DIR)
        ConfigInitializer.initialize(force=True)
        
        console.print(f"[green]✓[/green] Configuration reset to defaults")
        console.print(f"[green]✓[/green] Backup available at: {backup_path}")
        
    except Exception as e:
        console.print(f"[red]Error resetting configuration: {e}[/red]")
        raise typer.Exit(1)