"""Create and inspect real platform shortcuts inside an isolated cloud-runner home."""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def powershell_shortcut(path: Path) -> dict:
    escaped = str(path).replace("'", "''")
    script = (
        "$w=New-Object -ComObject WScript.Shell;"
        f"$s=$w.CreateShortcut('{escaped}');"
        "[PSCustomObject]@{TargetPath=$s.TargetPath;IconLocation=$s.IconLocation;"
        "WorkingDirectory=$s.WorkingDirectory;WindowStyle=$s.WindowStyle}|ConvertTo-Json -Compress"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30.0,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Could not inspect Windows shortcut {path}: {result.stdout}")
    return json.loads(result.stdout.strip())


def main() -> int:
    if (ROOT / "data").exists():
        raise RuntimeError("Refusing shortcut acceptance: source production data/ already exists.")

    runner_temp = Path(os.environ.get("RUNNER_TEMP", tempfile.gettempdir())).resolve()
    isolated = Path(tempfile.mkdtemp(prefix="ultron-cloud-shortcuts-", dir=runner_temp))
    owner_home = isolated / "Owner Home"
    application_home = isolated / "Ultron Application"
    desktop = owner_home / "Desktop"
    desktop.mkdir(parents=True)
    application_home.mkdir(parents=True)
    os.environ["HOME"] = str(owner_home)
    os.environ["USERPROFILE"] = str(owner_home)
    os.environ["APPDATA"] = str(owner_home / "AppData" / "Roaming")

    # Import only after the isolated owner environment is established.
    from backend.app import installer

    installer.ROOT = ROOT
    installer.APPLICATION_HOME = application_home
    installer.VENV_DIR = ROOT / ".venv"
    statuses: list[str] = []
    logs: list[str] = []
    engine = installer.InstallerEngine(statuses.append, logs.append)

    artifact_root = Path(
        os.environ.get("ULTRON_CLOUD_ARTIFACTS", runner_temp / "ultron-cloud-artifacts")
    ).resolve()
    artifact_root.mkdir(parents=True, exist_ok=True)
    report_path = artifact_root / f"shortcuts-{platform.system().lower()}.json"

    try:
        engine.create_shortcuts()
        generated_scripts = application_home / "app_shortcuts"
        if os.name == "nt":
            menu = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Ultron"
            expected = {
                menu / "Ultron.lnk": generated_scripts / "Start Ultron.cmd",
                menu / "Stop Ultron.lnk": generated_scripts / "Stop Ultron.cmd",
                menu / "Ultron Keys.lnk": generated_scripts / "Ultron Keys.cmd",
                desktop / "Ultron.lnk": generated_scripts / "Start Ultron.cmd",
            }
            icon = ROOT / "images" / "ultron_icon.ico"
            details = {}
            for shortcut, target in expected.items():
                if not shortcut.is_file():
                    raise RuntimeError(f"Windows shortcut was not created: {shortcut}")
                values = powershell_shortcut(shortcut)
                if str(target).casefold() != str(values.get("TargetPath", "")).casefold():
                    raise RuntimeError(f"Wrong Windows shortcut target: {shortcut}: {values}")
                if str(icon).casefold() not in str(values.get("IconLocation", "")).casefold():
                    raise RuntimeError(f"Wrong Windows shortcut icon: {shortcut}: {values}")
                if int(values.get("WindowStyle", 0)) != 7:
                    raise RuntimeError(f"Windows shortcut is not minimized: {shortcut}: {values}")
                details[shortcut.name] = values
            verified = sorted(str(path.relative_to(owner_home)) for path in expected)
        else:
            menu = owner_home / ".local" / "share" / "applications"
            expected = {
                menu / "ultron.desktop": generated_scripts / "start-ultron",
                menu / "ultron-stop.desktop": generated_scripts / "stop-ultron",
                menu / "ultron-keys.desktop": generated_scripts / "ultron-keys",
                desktop / "Ultron.desktop": generated_scripts / "start-ultron",
            }
            icon = ROOT / "images" / "ultron_icon.png"
            details = {}
            for shortcut, target in expected.items():
                if not shortcut.is_file():
                    raise RuntimeError(f"Ubuntu application entry was not created: {shortcut}")
                content = shortcut.read_text(encoding="utf-8")
                if f'Exec="{target}"' not in content:
                    raise RuntimeError(f"Wrong Ubuntu shortcut target: {shortcut}")
                if f"Icon={icon}" not in content:
                    raise RuntimeError(f"Wrong Ubuntu shortcut icon: {shortcut}")
                if "Terminal=false" not in content:
                    raise RuntimeError(f"Ubuntu shortcut would show a terminal: {shortcut}")
                details[shortcut.name] = {"target": str(target), "icon": str(icon), "terminal": False}
            verified = sorted(str(path.relative_to(owner_home)) for path in expected)

        if (ROOT / "data").exists():
            raise RuntimeError("Shortcut acceptance wrote into source production data/.")
        report = {
            "result": "verified_success",
            "platform": platform.platform(),
            "isolated_owner_home": True,
            "shortcuts": verified,
            "details": details,
            "real_credentials_used": False,
        }
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0
    finally:
        shutil.rmtree(isolated, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
