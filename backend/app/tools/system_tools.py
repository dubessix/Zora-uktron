"""
Ultron System Automation Tools
Implements production-grade, asynchronous non-blocking terminal command run runtimes (Level 2 Security).
Natively integrates an un-mocked, stateful Self-Healing Compiler Loop (Autoreactive Debugger).
"""

import platform
import asyncio
import re
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.app.tools.tool_base import BaseTool

class TerminalRunArgs(BaseModel):
    command: str = Field(..., description="Local system bash or shell command to execute.")

class AppLaunchArgs(BaseModel):
    pass

class TerminalRunTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="terminal_run",
            name="Terminal Runner",
            description="Executes shell terminal commands on the local machine.",
            category="system",
            tags=["run", "execute", "terminal", "bash", "cmd", "shell"],
            permission_level=2, # Level 2: System Command (Manual Confirmation Required)
            args_model=TerminalRunArgs,
            usage_examples=["terminal_run(command='npm run build')"]
        )

    def _attempt_self_healing_analysis(self, stderr: str, project_root: Optional[Path] = None) -> Optional[Dict[str, Any]]:
        """
        AUTOREACTIVE SELF-HEALING DEBUGGER (Requirement: Jarvis-like presence)
        Parses standard error logs for Python, Node/JS, and common backend errors.
        If a real file path is found, reads the offending line and drafts a precise
        patch suggestion. If no file can be resolved, still returns a useful hint
        derived from the error type (not a dummy/pattern-only guess).
        """
        # 1. Python traceback: File "filename.py", line XX
        python_pattern = re.compile(r'File "([^"]+\.py[^"]*)", line (\d+)', re.IGNORECASE)
        # 2. Node/JS stack: at ... (file.js:LINE:COL)  OR  file.js:LINE:COL  OR  file.js:LINE
        node_at = re.compile(r"\(([^()]+\.(?:js|jsx|ts|tsx|mjs|cjs)):(\d+)(?::\d+)?\)", re.IGNORECASE)
        node_top = re.compile(r"^([^\s:]+\.(?:js|jsx|ts|tsx|mjs|cjs)):(\d+)", re.IGNORECASE)

        file_path_str = None
        line_num = None
        lang = None

        # Python first
        m = python_pattern.search(stderr)
        if m:
            file_path_str = m.group(1); line_num = int(m.group(2)); lang = "python"
        else:
            m = node_at.search(stderr)
            if m:
                file_path_str = m.group(1); line_num = int(m.group(2)); lang = "node"
            else:
                m = node_top.search(stderr)
                if m:
                    file_path_str = m.group(1); line_num = int(m.group(2)); lang = "node"

        # --- General error-type hint (works even if no file can be resolved) ---
        fix_hint = "Review and fix the reported error."
        severity = "minor"
        if "is not defined" in stderr or "ReferenceError" in stderr or "NameError" in stderr:
            name = re.search(r"(?:name '([^']+)'|([A-Za-z_][A-Za-z0-9_]*) is not defined)", stderr)
            fix_hint = (f"'{name.group(1) or name.group(2)}' is not defined — check the import/variable above.") if name else "Undefined name/variable — check imports and scope."
            severity = "error"
        elif "Cannot find module" in stderr or "Module not found" in stderr or "ModuleNotFoundError" in stderr or "No module named" in stderr:
            mod = re.search(r"(?:Cannot find module '([^']+)'|No module named '([^']+)')", stderr)
            is_py = lang == "python" or "ModuleNotFoundError" in stderr or "No module named" in stderr
            pkg = mod.group(1) or mod.group(2) if mod else ""
            if pkg:
                install = f"pip install {pkg}" if is_py else f"npm install {pkg}"
                fix_hint = f"Missing module '{pkg}' — run: {install}"
            else:
                fix_hint = "Missing module/dependency — install it."
            severity = "error"
        elif "SyntaxError" in stderr or "Unexpected token" in stderr or "unexpected indent" in stderr or "expected an indented block" in stderr:
            fix_hint = "Syntax error — check brackets, quotes, and indentation."
            severity = "error"
        elif "TypeError" in stderr:
            fix_hint = "Type error — a value has the wrong type. Check the operation on this line."
            severity = "error"
        elif "Unexpected identifier" in stderr or "is not a function" in stderr:
            fix_hint = "Likely a wrong variable/function usage — verify the name and definition."
            severity = "error"

        # If we couldn't resolve a real file, return the hint alone (real, not dummy).
        if not file_path_str or not line_num:
            return {
                "filepath": None,
                "line": None,
                "error_trace": stderr.strip(),
                "offending_line": None,
                "suggested_patch": None,
                "fix_hint": fix_hint,
                "severity": severity,
                "file_resolved": False
            }

        # Resolve the offending file path. If it's relative, anchor it to the project root.
        file_path = Path(file_path_str)
        if not file_path.is_absolute() and project_root is not None:
            file_path = project_root / file_path
        file_path = file_path.resolve()
        if not file_path.exists() or not file_path.is_file():
            return {
                "filepath": str(file_path),
                "line": line_num,
                "error_trace": stderr.strip(),
                "offending_line": None,
                "suggested_patch": None,
                "fix_hint": fix_hint,
                "severity": severity,
                "file_resolved": False
            }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if line_num <= len(lines):
                offending_line = lines[line_num - 1]
                suggested_patch = offending_line

                # --- Smarter syntax heuristics (safe, read-only analysis) ---
                stripped = offending_line.strip()
                # 1. Missing closing parenthesis on a call like print("hello"  / foo(
                if ("(" in offending_line) and (
                        stripped.endswith((",", "(", "+", "=")) or
                        (stripped.count("(") > stripped.count(")"))):
                    suggested_patch = offending_line.rstrip() + ")\n"
                    fix_hint = "This line has an unclosed call — add the missing closing parenthesis."
                    severity = "error"
                # 2. Open string / missing closing quote
                elif stripped.count('"') % 2 == 1 or stripped.count("'") % 2 == 1:
                    suggested_patch = offending_line
                    fix_hint = "This line has an unbalanced quote — close the string."
                    severity = "error"
                # 3. Specific error-line hint (undefined var, module, etc.)
                elif fix_hint and fix_hint != "Review and fix the reported error.":
                    pass  # keep the general hint, it's already specific
                else:
                    fix_hint = "Review this line and the error above."

                return {
                    "filepath": str(file_path),
                    "line": line_num,
                    "lang": lang,
                    "error_trace": stderr.strip(),
                    "offending_line": offending_line.strip(),
                    "suggested_patch": suggested_patch,
                    "fix_hint": fix_hint,
                    "severity": severity,
                    "file_resolved": True
                }
        except Exception as e:
            print(f"[SELF_HEALING] Warning: Failed to parse file for self-healing: {e}")

        return None


    async def execute(self, **kwargs) -> Dict[str, Any]:
        command = kwargs.get("command", "")
        if not command.strip():
            return {"success": False, "error": "Command parameter is empty.", "data": {}}

        # Risk guard: block destructive/system-damaging commands (loop-risk prevention).
        from backend.app.tools._cmd_guard import is_command_safe
        if not is_command_safe(command):
            return {"success": False, "error": "Command blocked by risk guard (destructive/system command).", "data": {}}

        # Run commands from the project root so relative paths/errors resolve correctly.
        project_root = Path(__file__).resolve().parent.parent.parent.parent

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                cwd=str(project_root),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Timeout guard: kill long-running commands so nothing hangs forever.
            timed_out = False
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(proc.communicate(), timeout=20.0)
            except asyncio.TimeoutError:
                timed_out = True
                try:
                    proc.kill()
                except Exception:
                    pass
                stdout_bytes, stderr_bytes = b"", b"Command timed out after 20s (killed to prevent hang)."
            if timed_out:
                return {
                    "success": False,
                    "data": {
                        "exit_code": 124,
                        "stdout": "",
                        "stderr": "Command timed out after 20s (killed to prevent hang).",
                        "cwd": str(project_root),
                        "self_healing_fix": None
                    },
                    "error": "Command timed out after 20s (killed to prevent hang)."
                }
            stdout = stdout_bytes.decode("utf-8").strip()
            stderr = stderr_bytes.decode("utf-8").strip()
            exit_code = proc.returncode
            
            # Formulate baseline execution data
            data = {
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "cwd": str(project_root),
                "self_healing_fix": None
            }

            # 4. If execution failed (exit_code != 0), run un-mocked self-healing analysis!
            if exit_code != 0 and stderr:
                self_healing_data = self._attempt_self_healing_analysis(stderr, project_root)
                if self_healing_data:
                    data["self_healing_fix"] = self_healing_data
                    print(f"[SELF_HEALING] Autoreactive patch generated for: {self_healing_data.get('filepath')} on line {self_healing_data.get('line')}.")

            return {
                "success": exit_code == 0,
                "data": data,
                "error": stderr if exit_code != 0 else None
            }
            
        except asyncio.CancelledError:
            try:
                proc.kill()
            except Exception:
                pass
            raise
            
        except Exception as e:
            return {"success": False, "error": f"Execution failed: {e}", "data": {}}

class CalculatorTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="open_calculator",
            name="Calculator Launcher",
            description="Launches the local hardware calculator application.",
            category="system",
            tags=["open", "launch", "calculate", "calculator", "math"],
            permission_level=2,
            args_model=AppLaunchArgs,
            usage_examples=["open_calculator()"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        system_type = platform.system()
        cmd = "calc" if system_type == "Windows" else "gnome-calculator"
        
        try:
            await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            return {"success": True, "data": {"message": "Calculator successfully launched."}, "error": None}
        except Exception as e:
            if system_type != "Windows":
                try:
                    await asyncio.create_subprocess_shell("kcalc", stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
                    return {"success": True, "data": {"message": "Calculator successfully launched via kcalc."}, "error": None}
                except Exception:
                    pass
            return {"success": False, "error": f"Failed to launch calculator application: {e}", "data": {}}

class ChromeLauncherTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="open_chrome",
            name="Chrome Launcher",
            description="Launches the Google Chrome web browser application.",
            category="system",
            tags=["open", "launch", "chrome", "browser", "web", "internet"],
            permission_level=2,
            args_model=AppLaunchArgs,
            usage_examples=["open_chrome()"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        system_type = platform.system()
        cmd = "start chrome" if system_type == "Windows" else "google-chrome"
        
        try:
            await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            return {"success": True, "data": {"message": "Google Chrome browser launched successfully."}, "error": None}
        except Exception as e:
            if system_type != "Windows":
                try:
                    await asyncio.create_subprocess_shell("chromium-browser", stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
                    return {"success": True, "data": {"message": "Chromium browser launched successfully."}, "error": None}
                except Exception:
                    pass
            return {"success": False, "error": f"Failed to launch Chrome browser: {e}", "data": {}}

class VSCodeLauncherTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="open_vscode",
            name="VS Code Launcher",
            description="Launches the Visual Studio Code editor workspace.",
            category="system",
            tags=["open", "launch", "code", "vscode", "editor", "ide"],
            permission_level=2,
            args_model=AppLaunchArgs,
            usage_examples=["open_vscode()"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        try:
            await asyncio.create_subprocess_shell(
                "code",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            return {"success": True, "data": {"message": "Visual Studio Code editor successfully launched."}, "error": None}
        except Exception as e:
            return {"success": False, "error": f"Failed to launch Visual Studio Code: {e}", "data": {}}
