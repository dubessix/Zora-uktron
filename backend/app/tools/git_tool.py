"""
Ultron Real Git Status Tool
Asynchronously executes git bash commands via non-blocking subprocesses to analyze active repository branches,
modified files, and commit logs.
"""

import asyncio
from typing import Dict, Any
from pydantic import BaseModel
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
