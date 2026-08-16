"""Small cross-platform GUI installer and key editor for personal Ultron use."""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import threading
import venv
from pathlib import Path
from typing import Callable


SOURCE_ROOT = Path(__file__).resolve().parents[2]
SOURCE_MODE = (SOURCE_ROOT / "setup.py").is_file()
if SOURCE_MODE:
    ROOT = SOURCE_ROOT
    APPLICATION_HOME = SOURCE_ROOT
    VENV_DIR = SOURCE_ROOT / ".venv"
    ENV_EXAMPLE = SOURCE_ROOT / ".env.example"
else:
    from backend.app.install_paths import APPLICATION_HOME, ASSET_ROOT, ENV_EXAMPLE_PATH

    ROOT = ASSET_ROOT
    VENV_DIR = Path(sys.prefix)
    ENV_EXAMPLE = ENV_EXAMPLE_PATH
ENV_FILE = APPLICATION_HOME / ".env"

KEY_FIELDS = (
    ("Groq API key", "GROQ_API_KEY_1", True),
    ("Gemini API key", "GEMINI_API_KEY_1", True),
    ("NVIDIA API key", "NVIDIA_API_KEY_1", True),
    ("Tavily API key", "TAVILY_API_KEY", True),
    ("GitHub token", "GITHUB_TOKEN_1", True),
    ("GitHub username", "GITHUB_USERNAME_1", False),
)


def venv_python() -> Path:
    if not SOURCE_MODE:
        return Path(sys.executable).resolve()
    return VENV_DIR / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _read_env() -> tuple[list[str], dict[str, str]]:
    lines = ENV_FILE.read_text(encoding="utf-8").splitlines() if ENV_FILE.exists() else []
    values = {}
    for line in lines:
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return lines, values


def save_keys(updates: dict[str, str]) -> None:
    """Update only non-empty submitted values; preserve all unrelated env lines."""
    if not ENV_FILE.exists() and ENV_EXAMPLE.exists():
        shutil.copy2(ENV_EXAMPLE, ENV_FILE)
    lines, existing = _read_env()
    clean_updates = {key: value.strip() for key, value in updates.items() if value.strip()}
    if not clean_updates:
        return
    existing.update(clean_updates)
    managed = set(clean_updates)
    output = []
    written = set()
    for line in lines:
        if line and not line.lstrip().startswith("#") and "=" in line:
            key = line.split("=", 1)[0].strip()
            if key in managed:
                output.append(f"{key}={existing[key]}")
                written.add(key)
                continue
        output.append(line)
    for key in managed - written:
        output.append(f"{key}={existing[key]}")
    temporary = ENV_FILE.with_suffix(".tmp")
    temporary.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")
    os.replace(temporary, ENV_FILE)
    if os.name != "nt":
        ENV_FILE.chmod(0o600)


class InstallerEngine:
    def __init__(self, status: Callable[[str], None], log: Callable[[str], None]) -> None:
        self.status = status
        self.log = log

    def _run(self, command: list[str], label: str, timeout: float = 900.0) -> None:
        self.status(label)
        self.log(f"▶ {label}")
        process = subprocess.Popen(
            command,
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env={**os.environ, "ULTRON_HOME": str(APPLICATION_HOME)},
        )
        assert process.stdout is not None

        def pump_output() -> None:
            for line in process.stdout:
                text = line.rstrip()
                if text:
                    self.log(text)

        reader = threading.Thread(target=pump_output, daemon=True)
        reader.start()
        try:
            return_code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            process.kill()
            process.wait()
            raise RuntimeError(f"{label} timed out and was stopped.") from exc
        finally:
            reader.join(timeout=2.0)
        if return_code != 0:
            raise RuntimeError(f"{label} failed with status {return_code}.")

    def install(self) -> None:
        if sys.version_info < (3, 10):
            raise RuntimeError("Python 3.10 or newer is required.")
        if SOURCE_MODE:
            self.status("Creating the private Python environment…")
            if not venv_python().is_file():
                self.log("▶ Creating .venv")
                venv.EnvBuilder(with_pip=True, upgrade_deps=True).create(VENV_DIR)
            self._run(
                [str(venv_python()), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")],
                "Installing Ultron runtime packages…",
            )
        else:
            self.status("Installed Ultron package detected…")
            self.log("✓ Python package is already installed; runtime download skipped.")
        self._run(
            [str(venv_python()), "-m", "backend.app.cli", "setup"],
            "Creating private config, data, memory, and backups…",
        )
        self._run(
            [str(venv_python()), "-m", "backend.app.cli", "doctor"],
            "Running Ultron Doctor…",
        )
        self._run(
            [str(venv_python()), "-m", "backend.app.cli", "start", "--check"],
            "Checking packaged application assets…",
        )
        self.create_shortcuts()
        self.status("Ultron installation is ready.")
        self.log("✓ Installation finished. Add keys if needed, then click Start Ultron.")

    def _write_launch_scripts(self) -> dict[str, Path]:
        scripts = APPLICATION_HOME / "app_shortcuts"
        scripts.mkdir(parents=True, exist_ok=True)
        python = venv_python()
        if os.name == "nt":
            start = scripts / "Start Ultron.cmd"
            stop = scripts / "Stop Ultron.cmd"
            settings = scripts / "Ultron Keys.cmd"
            log = APPLICATION_HOME / "data" / "logs" / "launcher-ui.log"
            start.write_text(
                f'@echo off\r\ncd /d "{APPLICATION_HOME}"\r\n'
                f'if not exist "{log.parent}" mkdir "{log.parent}"\r\n'
                f'"{python}" -m backend.app.cli start >> "{log}" 2>&1\r\n',
                encoding="utf-8",
            )
            stop.write_text(
                f'@echo off\r\ncd /d "{APPLICATION_HOME}"\r\n'
                f'"{python}" -m backend.app.cli stop >> "{log}" 2>&1\r\n',
                encoding="utf-8",
            )
            settings.write_text(f'@echo off\r\n"{python}" -m backend.app.installer --keys\r\n', encoding="utf-8")
        else:
            start = scripts / "start-ultron"
            stop = scripts / "stop-ultron"
            settings = scripts / "ultron-keys"
            log = APPLICATION_HOME / "data" / "logs" / "launcher-ui.log"
            start.write_text(
                f'#!/bin/sh\ncd "{APPLICATION_HOME}"\nmkdir -p "{log.parent}"\n'
                f'exec "{python}" -m backend.app.cli start >> "{log}" 2>&1\n',
                encoding="utf-8",
            )
            stop.write_text(
                f'#!/bin/sh\ncd "{APPLICATION_HOME}"\nmkdir -p "{log.parent}"\n'
                f'exec "{python}" -m backend.app.cli stop >> "{log}" 2>&1\n',
                encoding="utf-8",
            )
            settings.write_text(f'#!/bin/sh\nexec "{python}" -m backend.app.installer --keys\n', encoding="utf-8")
            for path in (start, stop, settings):
                path.chmod(0o755)
        return {"start": start, "stop": stop, "settings": settings}

    def create_shortcuts(self) -> None:
        self.status("Creating application-menu shortcuts…")
        paths = self._write_launch_scripts()
        if platform.system() == "Windows":
            self._create_windows_shortcuts(paths)
        else:
            self._create_linux_shortcuts(paths)
        self.log("✓ Application shortcuts created.")

    def _create_windows_shortcuts(self, paths: dict[str, Path]) -> None:
        appdata = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
        menu = appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Ultron"
        menu.mkdir(parents=True, exist_ok=True)
        desktop = Path.home() / "Desktop"
        entries = {
            "Ultron": paths["start"],
            "Stop Ultron": paths["stop"],
            "Ultron Keys": paths["settings"],
        }
        for name, target in entries.items():
            destinations = [menu / f"{name}.lnk"]
            if name == "Ultron" and desktop.is_dir():
                destinations.append(desktop / "Ultron.lnk")
            for destination in destinations:
                destination_q = str(destination).replace("'", "''")
                target_q = str(target).replace("'", "''")
                root_q = str(APPLICATION_HOME).replace("'", "''")
                icon_q = str(venv_python()).replace("'", "''")
                command = (
                    "$w=New-Object -ComObject WScript.Shell;"
                    f"$s=$w.CreateShortcut('{destination_q}');"
                    f"$s.TargetPath='{target_q}';"
                    f"$s.WorkingDirectory='{root_q}';"
                    f"$s.IconLocation='{icon_q}';"
                    "$s.WindowStyle=7;"
                    "$s.Save()"
                )
                subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=20,
                )

    def _create_linux_shortcuts(self, paths: dict[str, Path]) -> None:
        applications = Path.home() / ".local" / "share" / "applications"
        applications.mkdir(parents=True, exist_ok=True)
        icon = ROOT / "images" / "ultron_ui_refined.png"
        entries = {
            "ultron.desktop": ("Ultron", paths["start"], False),
            "ultron-stop.desktop": ("Stop Ultron", paths["stop"], False),
            "ultron-keys.desktop": ("Ultron Keys", paths["settings"], False),
        }
        for filename, (name, executable, terminal) in entries.items():
            content = (
                "[Desktop Entry]\nType=Application\n"
                f"Name={name}\nExec=\"{executable}\"\nPath={APPLICATION_HOME}\n"
                f"Terminal={'true' if terminal else 'false'}\n"
                f"Icon={icon if icon.is_file() else 'applications-system'}\n"
                "Categories=Development;Utility;\n"
            )
            destination = applications / filename
            destination.write_text(content, encoding="utf-8")
            destination.chmod(0o755)
        desktop = Path.home() / "Desktop"
        if desktop.is_dir():
            shortcut = desktop / "Ultron.desktop"
            shutil.copy2(applications / "ultron.desktop", shortcut)
            shortcut.chmod(0o755)

    def start(self) -> None:
        if not venv_python().is_file():
            raise RuntimeError("Ultron is not installed yet. Click Install / Repair first.")
        options = {"cwd": str(APPLICATION_HOME), "env": {**os.environ, "ULTRON_HOME": str(APPLICATION_HOME)}}
        if os.name == "nt":
            options["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        else:
            options["start_new_session"] = True
        subprocess.Popen(
            [str(venv_python()), "-m", "backend.app.cli", "start"],
            **options,
        )
        self.status("Ultron start requested. The browser opens after both health checks pass.")

    def stop(self) -> None:
        if not venv_python().is_file():
            self.status("Ultron is not installed.")
            return
        self._run(
            [str(venv_python()), "-m", "backend.app.cli", "stop"],
            "Requesting a clean Ultron shutdown…",
            timeout=35.0,
        )
        self.status("Ultron is stopped.")


class InstallerWindow:
    def __init__(self, keys_only: bool = False) -> None:
        import tkinter as tk
        from tkinter import messagebox, scrolledtext, ttk

        self.tk = tk
        self.messagebox = messagebox
        self.root = tk.Tk()
        self.root.title("Ultron Personal V1 Setup")
        self.root.geometry("760x640")
        self.status_var = tk.StringVar(value="Ready. Nothing has been changed yet.")
        header = tk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w",
            padx=14,
            pady=12,
            font=("Segoe UI", 12, "bold"),
            bg="#101820",
            fg="#7dd3fc",
        )
        header.pack(fill="x")
        ttk.Label(self.root, text="API keys (empty fields keep existing values)").pack(anchor="w", padx=14, pady=(12, 4))
        self.entries = {}
        _, existing = _read_env()
        form = ttk.Frame(self.root)
        form.pack(fill="x", padx=14)
        for row, (label, key, secret) in enumerate(KEY_FIELDS):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=3)
            entry = ttk.Entry(form, show="•" if secret else "")
            entry.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=3)
            if not secret and existing.get(key):
                entry.insert(0, existing[key])
            elif secret and existing.get(key) and "your_" not in existing[key].lower():
                entry.insert(0, "")
            self.entries[key] = entry
        form.columnconfigure(1, weight=1)
        buttons = ttk.Frame(self.root)
        buttons.pack(fill="x", padx=14, pady=12)
        ttk.Button(buttons, text="Install / Repair", command=self.install).pack(side="left", padx=3)
        ttk.Button(buttons, text="Save Keys", command=self.save).pack(side="left", padx=3)
        ttk.Button(buttons, text="Start Ultron", command=self.start).pack(side="left", padx=3)
        ttk.Button(buttons, text="Stop Ultron", command=self.stop).pack(side="left", padx=3)
        self.progress = ttk.Progressbar(self.root, mode="indeterminate")
        self.progress.pack(fill="x", padx=14)
        self.log_widget = scrolledtext.ScrolledText(self.root, height=18, state="disabled", bg="#0b1117", fg="#d1fae5")
        self.log_widget.pack(fill="both", expand=True, padx=14, pady=12)
        self.engine = InstallerEngine(self.set_status, self.log)
        if keys_only:
            self.status_var.set("Update only the keys you want to change, then click Save Keys.")

    def set_status(self, text: str) -> None:
        self.root.after(0, self.status_var.set, text)

    def log(self, text: str) -> None:
        def append():
            self.log_widget.configure(state="normal")
            self.log_widget.insert("end", text + "\n")
            self.log_widget.see("end")
            self.log_widget.configure(state="disabled")
        self.root.after(0, append)

    def _worker(self, function: Callable[[], None]) -> None:
        def run():
            self.root.after(0, self.progress.start, 10)
            try:
                function()
            except Exception as exc:
                self.log(f"✗ {exc}")
                self.set_status(f"Stopped: {exc}")
                self.root.after(0, self.messagebox.showerror, "Ultron", str(exc))
            finally:
                self.root.after(0, self.progress.stop)
        threading.Thread(target=run, daemon=True).start()

    def save(self) -> None:
        values = {key: entry.get() for key, entry in self.entries.items()}
        try:
            save_keys(values)
            for entry in self.entries.values():
                entry.delete(0, "end")
            self.set_status("Keys saved privately. Empty fields were left unchanged.")
            self.log("✓ Key settings saved; secret values were not logged.")
        except Exception as exc:
            self.messagebox.showerror("Ultron", str(exc))

    def install(self) -> None:
        self.save()
        self._worker(self.engine.install)

    def start(self) -> None:
        self._worker(self.engine.start)

    def stop(self) -> None:
        self._worker(self.engine.stop)

    def run(self) -> None:
        self.root.mainloop()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--keys", action="store_true")
    args = parser.parse_args()
    try:
        InstallerWindow(keys_only=args.keys).run()
        return 0
    except ImportError:
        print("Tkinter is required for the graphical setup window.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
