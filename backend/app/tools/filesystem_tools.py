"""
Ultron Filesystem Tools
Implements production-grade, validated FileRead, FileWrite, and FindFiles tools with complete metadata parameters.
Uses high-performance recursive globbing while safely ignoring cache/virtual environment structures.
"""

import os
import datetime
from pathlib import Path
from typing import Dict, Any, Type, Optional
from pydantic import BaseModel, Field
from backend.app.tools.tool_base import BaseTool

# --- Validation Schemas ---

class FileReadArgs(BaseModel):
    filepath: str = Field(..., description="Target absolute or relative file path to read.")

class FileWriteArgs(BaseModel):
    filepath: str = Field(..., description="Target file path to write.")
    content: str = Field(..., description="Raw text content to write into the file.")

class FindFilesArgs(BaseModel):
    pattern: str = Field(..., description="Glob pattern or substring to search for (e.g. '*.pdf', 'resume').")
    search_root: Optional[str] = Field(".", description="The relative or absolute folder path to start searching from.")

# --- Tool Implementations ---

class FileReadTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="file_read",
            name="File Reader",
            description="Reads and retrieves text contents of local files.",
            category="filesystem",
            tags=["file", "read", "load", "view"],
            permission_level=0, # Level 0: Read-Only (no confirmation)
            args_model=FileReadArgs,
            usage_examples=["file_read(filepath='src/App.jsx')"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        filepath = kwargs.get("filepath", "")
        path = Path(filepath).resolve()
        
        if not path.exists():
            return {"success": False, "error": f"File does not exist: {filepath}", "data": {}}
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                return {"success": True, "data": {"content": f.read()}, "error": None}
        except Exception as e:
            return {"success": False, "error": f"Failed to read file: {e}", "data": {}}

class FileWriteTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="file_write",
            name="File Writer",
            description="Writes text contents into local files. Overwrites existing contents.",
            category="filesystem",
            tags=["file", "write", "save", "create"],
            permission_level=1, # Level 1: Write (no confirmation)
            args_model=FileWriteArgs,
            usage_examples=["file_write(filepath='src/notes.txt', content='Active metrics')"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        filepath = kwargs.get("filepath", "")
        content = kwargs.get("content", "")
        path = Path(filepath).resolve()
        
        try:
            # Ensure parent directories exist
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "data": {"message": f"Successfully wrote to file: {filepath}"}, "error": None}
        except Exception as e:
            return {"success": False, "error": f"Failed to write file: {e}", "data": {}}

class FindFilesTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="find_files",
            name="File Finder",
            description="Searches for files recursively inside the workspace using glob or text pattern checks.",
            category="filesystem",
            tags=["file", "find", "search", "glob", "locate"],
            permission_level=0, # Level 0: Read-Only (no confirmation)
            args_model=FindFilesArgs,
            usage_examples=["find_files(pattern='*.pdf')"]
        )
        self.workspace_root = Path(__file__).resolve().parent.parent.parent.parent

    async def execute(self, **kwargs) -> Dict[str, Any]:
        pattern = kwargs.get("pattern", "").strip()
        search_root_str = kwargs.get("search_root", ".")
        
        root_path = Path(search_root_str).resolve()
        if not root_path.exists():
            root_path = (self.workspace_root / search_root_str).resolve()
            if not root_path.exists():
                return {"success": False, "error": f"Search root folder '{search_root_str}' does not exist.", "data": {}}

        if not pattern:
            return {"success": False, "error": "Pattern parameter cannot be empty.", "data": {}}

        results = []
        skip_dirs = {".git", "venv", ".arena", "__pycache__", "node_modules", "build", "dist", "data"}

        try:
            # If pattern doesn't contain wildcards, assume substring match
            is_glob = "*" in pattern or "?" in pattern or "[" in pattern
            
            # Walk and glob manually to safely ignore cache/venv folders on any OS
            for root, dirs, files in os.walk(root_path):
                # Prune cache/virtual environments recursively
                dirs[:] = [d for d in dirs if d not in skip_dirs]
                
                for file in files:
                    file_path = Path(root) / file
                    file_rel = str(file_path.relative_to(self.workspace_root))
                    
                    matched = False
                    if is_glob:
                        # Glob match
                        matched = file_path.match(pattern)
                    else:
                        # Substring match
                        matched = pattern.lower() in file.lower()

                    if matched:
                        try:
                            stat = file_path.stat()
                            mtime = datetime.datetime.fromtimestamp(stat.st_mtime, datetime.timezone.utc).isoformat()
                            results.append({
                                "name": file,
                                "filepath": file_rel,
                                "size_kb": f"{stat.st_size / 1024:.1f} KB",
                                "modified_at": mtime
                            })
                        except OSError:
                            continue

            return {
                "success": True,
                "data": {
                    "pattern": pattern,
                    "matches_count": len(results),
                    "matches": results
                },
                "error": None
            }
        except Exception as e:
            return {"success": False, "error": f"File finder search aborted: {e}", "data": {}}
