"""
Ultron Multi-Service Launcher Engine
Launches local FastAPI backend and Vite frontend compilers concurrently.
Manages native subprocesses, handles Ctrl+C signals, and launches default browser.
Natively verified on Windows 11 and Ubuntu 24.04.
"""

import os
import sys
import socket
import platform
import subprocess
import signal
import time
import webbrowser
from pathlib import Path
from threading import Thread

# Pathing parameters
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Service ports (kept in sync with config.yaml / backend)
BACKEND_PORT = 8000
FRONTEND_PORT = 5173

class ServiceLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.is_shutting_down = False

    def log(self, service: str, message: str, color_code: str = "32"):
        """Print stylized system logs to standard stdout."""
        print(f"\033[1;{color_code}m[{service}]\033[0m {message}")

    def stream_output(self, process, name: str, color_code: str):
        """Asynchronously pipe stdout/stderr streams to current console output."""
        try:
            for line in iter(process.stdout.readline, ""):
                if not line:
                    break
                self.log(name, line.strip(), color_code)
        except Exception:
            pass

    def check_node_modules(self) -> bool:
        """Validate if npm installation was conducted on frontend packages."""
        return (FRONTEND_DIR / "node_modules").exists()

    @staticmethod
    def check_port_availability(port: int, host: str = "127.0.0.1") -> bool:
        """Return True if a TCP port is free to bind on the given host."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return True
            except OSError:
                return False

    def preflight_port_check(self) -> bool:
        """Ensure both service ports are free BEFORE booting, with clear errors."""
        ok = True
        for name, port in [("backend (8000)", BACKEND_PORT), ("frontend (5173)", FRONTEND_PORT)]:
            if self.check_port_availability(port):
                self.log("Launcher", f"Port {name} is free. Proceeding.", "32")
            else:
                self.log("Launcher", f"Port {name} is ALREADY IN USE. "
                                     "Close the occupying process (or an existing Ultron instance) and retry.", "31")
                ok = False
        return ok

    def run(self):
        """Execute concurrent bootstrap sequences."""
        self.log("Launcher", "Initializing Ultron Cross-Platform Orchestrator...", "35")

        # 0. Preflight: verify service ports are free before booting anything
        if not self.preflight_port_check():
            self.log("Launcher", "Aborting launch: required ports are occupied.", "31")
            sys.exit(1)

        # 1. Run node package audit
        if not self.check_node_modules():
            self.log("Launcher", "node_modules not found in /frontend. Executing npm install...", "33")
            try:
                subprocess.run(
                    ["npm", "install"],
                    cwd=str(FRONTEND_DIR),
                    shell=platform.system() == "Windows",
                    check=True
                )
            except subprocess.CalledProcessError as e:
                self.log("Launcher", f"Failed to complete npm install: {e}", "31")
                sys.exit(1)

        # 2. Configure signal interrupters
        signal.signal(signal.SIGINT, self.shutdown_handler)
        signal.signal(signal.SIGTERM, self.shutdown_handler)

        # 3. Boot Backend Process (FastAPI via Uvicorn)
        self.log("Launcher", "Booting FastAPI Application server...", "35")
        backend_cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(BACKEND_PORT)
        ]
        
        # Create dedicated subprocess configurations for clean OS termination
        creation_flags = 0
        if platform.system() == "Windows":
            # Directs subprocess to run in its own console group
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

        self.backend_process = subprocess.Popen(
            backend_cmd,
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=creation_flags,
            preexec_fn=os.setsid if platform.system() != "Windows" else None
        )

        # Span worker thread to stream logging
        Thread(
            target=self.stream_output,
            args=(self.backend_process, "FastAPI", "34"),
            daemon=True
        ).start()

        # 4. Boot Frontend Process (Vite Compilers)
        self.log("Launcher", "Launching React + Vite Asset Compiler...", "35")
        
        frontend_cmd = ["npm", "run", "dev"]
        self.frontend_process = subprocess.Popen(
            frontend_cmd,
            cwd=str(FRONTEND_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=platform.system() == "Windows",
            creationflags=creation_flags,
            preexec_fn=os.setsid if platform.system() != "Windows" else None
        )

        Thread(
            target=self.stream_output,
            args=(self.frontend_process, "Vite", "36"),
            daemon=True
        ).start()

        # 5. Delay browser launch until ports stabilize
        time.sleep(1.5)
        self.log("Launcher", "Orchestration fully aligned. Launching user viewport...", "35")
        webbrowser.open(f"http://127.0.0.1:{FRONTEND_PORT}")

        # 6. Keep main launcher execution alive
        try:
            while not self.is_shutting_down:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            self.shutdown_handler(None, None)

    def shutdown_handler(self, signum, frame):
        """Gracefully terminate child processes to prevent local port lockouts."""
        if self.is_shutting_down:
            return
        self.is_shutting_down = True
        self.log("Launcher", "\nInitiating graceful teardown sequences of sub-services...", "31")

        # Terminate frontend compiler process group
        if self.frontend_process:
            self.log("Launcher", "Killing Vite compiler processes...", "31")
            self.kill_process_tree(self.frontend_process)

        # Terminate backend REST/WS process group
        if self.backend_process:
            self.log("Launcher", "Killing FastAPI application instances...", "31")
            self.kill_process_tree(self.backend_process)

        self.log("Launcher", "Teardown completed cleanly. System offline.", "35")
        sys.exit(0)

    def kill_process_tree(self, proc):
        """Cross-platform utility to terminate full process tree groups."""
        try:
            if platform.system() == "Windows":
                # On Windows, kill process groups using windows tasks kill utility
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                # On Linux/Ubuntu, send SIGTERM signal to progress group
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except Exception:
            try:
                proc.terminate()
            except Exception:
                pass

if __name__ == "__main__":
    launcher = ServiceLauncher()
    launcher.run()
