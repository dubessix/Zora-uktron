"""
Ultron Real Git Status Tool
Asynchronously executes git bash commands via non-blocking subprocesses to analyze active repository branches,
modified files, and commit logs.
"""

import asyncio
from typing import Dict, Any
from pydantic import BaseModel, Field
from backend.app.tools.tool_base import BaseTool

class GitArgs(BaseModel):
    pass # No input arguments required for general git status check

class GitStatusTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="git_status",
            name="Git Repository Watcher",
            description="Analyzes the current Git repository branch, uncommitted files, and modifications.",
            category="developer",
            tags=["git", "status", "branch", "commit", "uncommitted", "modified"],
            permission_level=0, # Level 0: Read-Only (no confirmation)
            args_model=GitArgs,
            usage_examples=["git_status()"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        try:
            # 1. Fetch current active branch
            proc_branch = await asyncio.create_subprocess_shell(
                "git branch --show-current",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout_b, _ = await proc_branch.communicate()
            branch_name = stdout_b.decode("utf-8").strip() or "main"
            
            # 2. Fetch modified uncommitted files (real, no fake fallback)
            proc_status = await asyncio.create_subprocess_shell(
                "git status --porcelain",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout_s, _ = await proc_status.communicate()
            status_lines = stdout_s.decode("utf-8").splitlines()
            
            uncommitted_files = []
            for line in status_lines[:10]:  # Capture top 10 modified files
                if line.strip():
                    parts = line.strip().split(maxsplit=1)
                    if len(parts) == 2:
                        uncommitted_files.append(parts[1])

            # 3. Fetch the real last commit message (P0-7: no hardcoded fake commit)
            proc_log = await asyncio.create_subprocess_shell(
                "git log -1 --pretty=%s",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout_l, _ = await proc_log.communicate()
            last_commit = stdout_l.decode("utf-8").strip()

            return {
                "success": True,
                "data": {
                    "branch": branch_name,
                    "uncommitted_files": uncommitted_files,
                    "last_commit": last_commit  # real, or "" if none
                },
                "error": None
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to execute git repository status: {e}", "data": {}}


class GitCloneArgs(BaseModel):
    url: str = Field(..., description="Git repository URL to clone.")
    directory: str = Field(".", description="Target directory to clone into.")

class GitCloneTool(BaseTool):
    """Developer automation: clone a repo (download code) via git."""

    def __init__(self) -> None:
        super().__init__(
            tool_id="git_clone",
            name="Git Clone",
            description="Clones a git repository (downloads code) into a local directory.",
            category="developer",
            tags=["git", "clone", "download", "repo"],
            permission_level=2,  # requires confirmation
            args_model=GitCloneArgs,
            usage_examples=["git_clone(url='https://github.com/org/repo.git', directory='repos')"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        url = kwargs.get("url", "").strip()
        directory = kwargs.get("directory", ".").strip()
        if not url:
            return {"success": False, "error": "url required", "data": {}}
        if any(ch in (url + directory) for ch in ";|&`$(){}<>"):
            return {"success": False, "error": "Unsafe characters blocked.", "data": {}}

        from backend.app.security.url_guard import validate_public_url
        if not url.lower().startswith("https://"):
            return {"success": False, "error": "Git clone URL must use public HTTPS.", "data": {}}
        url_ok, url_reason = validate_public_url(url)
        if not url_ok:
            return {"success": False, "error": f"Git clone URL blocked: {url_reason}", "data": {}}

        from pathlib import Path
        from backend.app.security.path_guard import check_path
        destination = Path(directory).expanduser().resolve(strict=False)
        decision = check_path(str(destination))
        if not decision["safe"]:
            return {"success": False, "error": f"Clone destination blocked ({decision['reason']}): {destination}", "data": {}}
        try:
            proc = await asyncio.create_subprocess_exec(
                "git", "-c", "http.followRedirects=false", "clone", url, directory,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            out, err = await asyncio.wait_for(proc.communicate(), timeout=120)
            code = proc.returncode
            if code == 0:
                return {"success": True, "data": {"message": f"Cloned {url} into {directory}"}, "error": None}
            return {"success": False, "error": (err.decode() or "clone failed")[:200], "data": {}}
        except asyncio.TimeoutError:
            return {"success": False, "error": "Clone timed out (120s).", "data": {}}
        except Exception as e:
            return {"success": False, "error": f"Clone failed: {e}", "data": {}}
