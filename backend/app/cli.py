"""
Ultron CLI Manager
Provides global administration, setup wizards, diagnostics, and launch routines.
Supports Windows 11 & Linux Ubuntu 24.04 natively.
"""

import os
import sys
import platform
import shutil
import socket
import click
import yaml
import psutil

from backend.app.install_paths import (
    APPLICATION_HOME,
    ASSET_ROOT,
    CONFIG_PATH,
    ENV_EXAMPLE_PATH,
    ENV_PATH,
    FRONTEND_DIR,
    LAUNCHER_PATH,
    ensure_user_config,
)

# Runtime state is writable under the source checkout or the user's ULTRON_HOME.
BASE_DIR = APPLICATION_HOME

def check_port_availability(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a specific TCP port is open locally."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False

def load_yaml_config():
    """Load configuration variables safely."""
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        try:
            return yaml.safe_load(f) or {}
        except yaml.YAMLError:
            return {}

@click.group()
def main():
    """ULTRON V1: Core Developer Partner & Companion CLI Administrative Engine."""
    pass

@main.command()
def version():
    """Print the current active version of the Ultron system."""
    config = load_yaml_config()
    version_str = config.get("ultron", {}).get("version", "1.0.0")
    click.echo(click.style(f"ULTRON Core Engine — Version: {version_str}", fg="cyan", bold=True))

@main.command()
@click.option("--force", is_flag=True, help="Re-check/create runtime directories without deleting user data.")
def setup(force):
    """Create a writable personal runtime home from bundled installation assets."""
    click.echo(click.style("=== ULTRON V1 INITIALIZATION SETUP ===", fg="cyan", bold=True))

    BASE_DIR.mkdir(parents=True, exist_ok=True)
    required_dirs = [
        BASE_DIR / "data" / "memory",
        BASE_DIR / "data" / "logs",
        BASE_DIR / "data" / "cache",
    ]
    for directory in required_dirs:
        existed = directory.exists()
        directory.mkdir(parents=True, exist_ok=True)
        if force or not existed:
            click.echo(f"Created system directory: {directory.relative_to(BASE_DIR)}")

    try:
        user_config = ensure_user_config(overwrite=False)
        click.echo(f"Configuration ready: {user_config}")
    except OSError as exc:
        raise click.ClickException(f"Could not install default config: {exc}") from exc

    # Never overwrite an existing .env: it may contain the owner's live keys.
    if not ENV_PATH.exists():
        try:
            if ENV_EXAMPLE_PATH.is_file():
                shutil.copy2(ENV_EXAMPLE_PATH, ENV_PATH)
            else:
                ENV_PATH.write_text(
                    "GROQ_API_KEY_1=your_groq_api_key_1_here\n"
                    "GEMINI_API_KEY_1=your_gemini_api_key_1_here\n"
                    "NVIDIA_API_KEY_1=your_nvidia_api_key_1_here\n",
                    encoding="utf-8",
                )
        except OSError as exc:
            raise click.ClickException(f"Could not create .env template: {exc}") from exc
        click.echo(click.style("Created secure API environment key template (.env)", fg="green"))
    else:
        click.echo(click.style("Existing secure environment keys (.env) preserved.", fg="yellow"))

    click.echo(click.style("\nSetup completed. Configure .env, then run 'ultron doctor'.", fg="green", bold=True))

@main.command()
def doctor():
    """Execute complete software-dependency, API, hardware, and port health diagnostics."""
    click.echo(click.style("=== ULTRON SYSTEM DIAGNOSTIC ANALYSIS (DOCTOR) ===", fg="cyan", bold=True))
    all_green = True
    warning_count = 0

    # 1. Host Hardware Analysis
    click.echo("\n[1/5] Checking Hardware Environment Constraints...")
    total_ram_gb = psutil.virtual_memory().total / (1024 ** 3)
    click.echo(f"  - Detected OS: {platform.system()} ({platform.release()})")
    click.echo(f"  - Detected CPU Cores: {psutil.cpu_count(logical=True)} logical cores")
    click.echo(f"  - System RAM Capacity: {total_ram_gb:.2f} GB")
    if total_ram_gb < 7.5:
        warning_count += 1
        click.echo(click.style("  ⚠️ Warning: Available RAM is below 8GB. Strictly avoid local LLM/STT executions.", fg="yellow"))
    else:
        click.echo(click.style("  ✓ Hardware profiles comply with 8GB RAM host standard.", fg="green"))

    # 2. Key Binary Dependencies Check
    click.echo("\n[2/5] Checking Binary Executables on PATH...")
    binaries = ["node", "npm", "git"]
    if platform.system() != "Windows":
        binaries.append("ffmpeg")
    else:
        # Ffmpeg validation warning for Windows audio conversion
        binaries.append("ffmpeg")

    for binary in binaries:
        path_check = shutil.which(binary) if hasattr(shutil, "which") else None
        binary_path = path_check
        if binary_path:
            click.echo(f"  ✓ {binary:<8}: Found at {binary_path}")
        else:
            if binary == "ffmpeg":
                warning_count += 1
                click.echo(click.style(f"  ⚠️ {binary:<8}: Missing. Voice converter requires ffmpeg added to PATH.", fg="yellow"))
            else:
                click.echo(click.style(f"  ✗ {binary:<8}: Missing. Please install {binary} to proceed.", fg="red"))
                all_green = False

    # 3. Local Port Availability
    click.echo("\n[3/5] Verifying Port Configurations...")
    config = load_yaml_config()
    backend_port = config.get("server", {}).get("backend_port", 8000)
    frontend_port = config.get("server", {}).get("frontend_port", 5173)

    for port, name in [(backend_port, "FastAPI Backend"), (frontend_port, "React Frontend")]:
        available = check_port_availability(port)
        if available:
            click.echo(f"  ✓ Port {port:<5}: Available for {name}")
        else:
            click.echo(click.style(f"  ✗ Port {port:<5}: Occupied. Cannot boot {name} service.", fg="red"))
            all_green = False

    # 4. Storage & SQLite Access Verification
    click.echo("\n[4/5] Checking Storage & Databases Access...")
    db_dir = BASE_DIR / "data" / "memory"
    if db_dir.exists():
        try:
            test_file = db_dir / ".doctor_write_test"
            test_file.touch()
            test_file.unlink()
            click.echo("  ✓ Database Directory: Read-Write permissions verified successfully.")
        except OSError:
            click.echo(click.style("  ✗ Database Directory: Read-Write access denied.", fg="red"))
            all_green = False
    else:
        click.echo(click.style("  ⚠️ Database Directory: Missing. Please run 'ultron setup' first.", fg="yellow"))
        all_green = False

    # 5. Config Profiles Audit
    click.echo("\n[5/5] Auditing Configuration Profiles...")
    config_valid = bool(config) and isinstance(config.get("server"), dict) and isinstance(config.get("ai"), dict)
    if CONFIG_PATH.is_file() and config_valid:
        click.echo(f"  ✓ config.yaml: Parsed required sections from {CONFIG_PATH}.")
    elif CONFIG_PATH.is_file():
        click.echo(click.style("  ✗ config.yaml: Present but malformed or missing server/ai sections.", fg="red"))
        all_green = False
    else:
        click.echo(click.style("  ✗ config.yaml: Missing! System requires a valid configuration file.", fg="red"))
        all_green = False

    if all_green and warning_count:
        click.echo(click.style(
            f"\n⚠ CORE CHECKS PASSED WITH {warning_count} WARNING(S). "
            "Review optional hardware/media limitations above before daily use.",
            fg="yellow",
            bold=True,
        ))
    elif all_green:
        click.echo(click.style("\n✓ DIAGNOSTICS PASSED: Required checks succeeded.", fg="green", bold=True))
    else:
        click.echo(click.style("\n✗ DIAGNOSTICS FAILED: Please resolve outstanding issues listed above.", fg="red", bold=True))
        sys.exit(1)

@main.command()
@click.option("--restore", is_flag=True, help="Restore the database from a backup file.")
@click.option("--path", type=str, default=None, help="Backup file path to restore from (with --restore).")
@click.option("--yes", is_flag=True, help="Confirm the exact local restore non-interactively.")
def backup(restore, path, yes):
    """Back up or explicitly restore the local database (durability)."""
    from backend.app.database.backup import backup_database, restore_database
    if restore:
        if not path:
            click.echo(click.style("Error: --path <backup.db> is required with --restore.", fg="red"))
            return
        if not yes and not click.confirm(f"Restore the exact approved backup '{path}'?"):
            click.echo("Restore cancelled; database was not changed.")
            return
        result = restore_database(path)
        if result["success"]:
            click.echo(click.style(f"✓ Restored from {result['data']['restored_from']} (safety copy: {result['data']['safety_backup']})", fg="green"))
        else:
            click.echo(click.style(f"✗ Restore failed: {result['error']}", fg="red"))
        return
    result = backup_database()
    if result["success"]:
        click.echo(click.style(f"✓ Backup created: {result['data']['backup_path']} ({result['data']['bytes']} bytes, verified)", fg="green"))
    else:
        click.echo(click.style(f"✗ Backup failed: {result['error']}", fg="red"))

@main.command()
def integrity():
    """Check the local database integrity (durability)."""
    from backend.app.database.backup import check_integrity
    report = check_integrity()["data"]
    if report["valid"]:
        click.echo(click.style("✓ Database integrity OK.", fg="green"))
    else:
        click.echo(click.style(f"✗ Integrity issues: {report.get('integrity')} {report.get('error')}", fg="red"))
    for table, count in (report.get("tables") or {}).items():
        click.echo(f"  {table}: {count} rows")

@main.command()
@click.option("--check", "check_only", is_flag=True, help="Verify installed launch assets without starting services.")
def start(check_only):
    """Launch the installed backend/frontend bundle through the master launcher."""
    click.echo(click.style("Bootstrapping services...", fg="cyan"))
    import subprocess

    required_assets = [
        LAUNCHER_PATH,
        CONFIG_PATH,
        FRONTEND_DIR / "package.json",
        FRONTEND_DIR / "package-lock.json",
        FRONTEND_DIR / "src" / "App.jsx",
    ]
    missing = [str(path) for path in required_assets if not path.is_file()]
    if missing:
        raise click.ClickException(
            "Installation is incomplete; missing assets: " + ", ".join(missing)
        )
    if check_only:
        click.echo(click.style(
            f"Installation assets verified at {ASSET_ROOT}.",
            fg="green",
            bold=True,
        ))
        return

    env = os.environ.copy()
    env.setdefault("ULTRON_HOME", str(APPLICATION_HOME))
    completed = subprocess.run(
        [sys.executable, str(LAUNCHER_PATH)],
        cwd=str(ASSET_ROOT),
        env=env,
        check=False,
    )
    if completed.returncode != 0:
        raise click.ClickException(
            f"Launcher exited with status {completed.returncode}. See service logs above."
        )

if __name__ == "__main__":
    main()
