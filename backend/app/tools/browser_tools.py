"""
Ultron Production-Grade Browser Tools
Implements un-mocked WebBrowser controls: Open URL, Open Tab, Close Tab, Refresh, Back, Forward, and Close Browser.
Uses lightweight cross-platform shell key senders (xdotool on Linux, powershell on Windows)
to trigger active browser controls without heavy Selenium/Playwright dependencies, protecting 8GB RAM bounds.
"""

import webbrowser
import httpx
import platform
import asyncio
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel, Field
from backend.app.tools.tool_base import BaseTool

# --- Validation Schemas ---

class OpenUrlArgs(BaseModel):
    url: str = Field(..., description="Target web URL address to open.")

class EmptyArgs(BaseModel):
    pass

class DownloadUrlArgs(BaseModel):
    url: str = Field(..., description="Target asset URL address to download.")
    save_path: str = Field(..., description="Target local destination file path.")

class ReadPageArgs(BaseModel):
    url: str = Field(..., description="Target web page URL address to read and parse.")

# --- Helper Key Senders ---

async def send_browser_shortcut(key_combo: str) -> bool:
    """Sends native system-wide keyboard shortcuts to control the active browser window."""
    system_type = platform.system()
    try:
        if system_type == "Windows":
            # Send keys via powershell wscript.shell interface
            powershell_cmd = f"powershell -c \"$wshell = New-Object -ComObject wscript.shell; $wshell.SendKeys('{key_combo}')\""
            proc = await asyncio.create_subprocess_shell(
                powershell_cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await proc.wait()
            return True
        else:
            # Send keys via xdotool utility on Linux Ubuntu
            # Map Windows key notation to xdotool syntax
            xdo_key = key_combo.lower()
            if "^w" in xdo_key or "ctrl+w" in xdo_key:
                cmd = "xdotool key ctrl+w"
            elif "f5" in xdo_key:
                cmd = "xdotool key F5"
            elif "%{left}" in xdo_key or "alt+left" in xdo_key:
                cmd = "xdotool key alt+Left"
            elif "%{right}" in xdo_key or "alt+right" in xdo_key:
                cmd = "xdotool key alt+Right"
            else:
                return False
                
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await proc.wait()
            return True
    except Exception:
        return False

# --- Tool Implementations ---

class OpenUrlTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="open_url",
            name="URL Opener",
            description="Opens a requested URL web page inside the default Chrome browser.",
            category="browser",
            tags=["browser", "url", "open", "chrome", "web"],
            permission_level=1, # Level 1: Automatically allowed (Requirement: Phase 5)
            args_model=OpenUrlArgs,
            usage_examples=["open_url(url='https://github.com')"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        url = kwargs.get("url", "")
        try:
            webbrowser.open(url)
            return {"success": True, "data": {"message": f"Successfully launched URL in default browser: {url}"}, "error": None}
        except Exception as e:
            return {"success": False, "error": f"Failed to launch URL: {e}", "data": {}}

class OpenNewTabTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="open_new_tab",
            name="New Tab Opener",
            description="Opens a requested URL web page inside a new browser tab.",
            category="browser",
            tags=["browser", "tab", "new", "chrome"],
            permission_level=1, # Level 1: Automatically allowed (Requirement: Phase 5)
            args_model=OpenUrlArgs,
            usage_examples=["open_new_tab(url='https://stackoverflow.com')"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        url = kwargs.get("url", "")
        try:
            webbrowser.open_new_tab(url)
            return {"success": True, "data": {"message": f"Successfully launched new browser tab: {url}"}, "error": None}
        except Exception as e:
            return {"success": False, "error": f"Failed to open tab: {e}", "data": {}}

class CloseCurrentTabTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="close_tab",
            name="Tab Closer",
            description="Closes the currently active browser tab using system keyboard controls. Never closes browser window.",
            category="browser",
            tags=["browser", "tab", "close", "remove"],
            permission_level=2, # Level 2: Requires manual confirmation
            args_model=EmptyArgs,
            usage_examples=["close_tab()"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        # Sends Ctrl+W macro shortcut natively to close active tab
        success = await send_browser_shortcut("^w" if platform.system() == "Windows" else "ctrl+w")
        if success:
            return {"success": True, "data": {"message": "Active browser tab closed successfully."}, "error": None}
        return {"success": False, "error": "Failed to close active tab. System command macro error.", "data": {}}

class RefreshPageTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="refresh_page",
            name="Page Refresher",
            description="Refreshes the active browser tab page natively.",
            category="browser",
            tags=["browser", "refresh", "reload"],
            permission_level=1, # Level 1
            args_model=EmptyArgs,
            usage_examples=["refresh_page()"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        success = await send_browser_shortcut("{F5}" if platform.system() == "Windows" else "f5")
        if success:
            return {"success": True, "data": {"message": "Browser page refreshed successfully."}, "error": None}
        return {"success": False, "error": "Failed to execute page refresh.", "data": {}}

class BackTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="browser_back",
            name="Browser Navigation Back",
            description="Navigates back to the previous page in the browser history.",
            category="browser",
            tags=["browser", "back", "previous"],
            permission_level=1, # Level 1
            args_model=EmptyArgs,
            usage_examples=["browser_back()"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        success = await send_browser_shortcut("%{LEFT}" if platform.system() == "Windows" else "alt+left")
        if success:
            return {"success": True, "data": {"message": "Navigated back successfully."}, "error": None}
        return {"success": False, "error": "Failed to navigate back.", "data": {}}

class ForwardTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="browser_forward",
            name="Browser Navigation Forward",
            description="Navigates forward to the next page in the browser history.",
            category="browser",
            tags=["browser", "forward", "next"],
            permission_level=1, # Level 1
            args_model=EmptyArgs,
            usage_examples=["browser_forward()"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        success = await send_browser_shortcut("%{RIGHT}" if platform.system() == "Windows" else "alt+right")
        if success:
            return {"success": True, "data": {"message": "Navigated forward successfully."}, "error": None}
        return {"success": False, "error": "Failed to navigate forward.", "data": {}}

class CloseBrowserTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="close_browser",
            name="Browser Window Closer",
            description="Closes the entire browser window recursively. Requires explicit confirmation.",
            category="browser",
            tags=["browser", "close", "quit", "window"],
            permission_level=3, # Level 3: Dangerous (Requires confirmation)
            args_model=EmptyArgs,
            usage_examples=["close_browser()"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        # Sends Alt+F4 macro to close browser window natively
        success = await send_browser_shortcut("%{F4}" if platform.system() == "Windows" else "alt+f4")
        if success:
            return {"success": True, "data": {"message": "Entire browser window closed successfully."}, "error": None}
        return {"success": False, "error": "Failed to close browser window.", "data": {}}

class DownloadFileTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="download_file",
            name="Asset Downloader",
            description="Downloads a remote file asset directly to the local directory path asynchronously.",
            category="browser",
            tags=["browser", "download", "fetch", "file"],
            permission_level=1,
            args_model=DownloadUrlArgs,
            usage_examples=["download_file(url='https://example.com/logo.png', save_path='data\\logo.png')"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        url = kwargs.get("url", "")
        save_path = Path(kwargs.get("save_path", "")).resolve()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=20.0)
                if response.status_code == 200:
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(save_path, "wb") as f:
                        f.write(response.content)
                    return {"success": True, "data": {"message": f"Asset downloaded successfully to {save_path}"}, "error": None}
                else:
                    return {"success": False, "error": f"Download API returned status code: {response.status_code}", "data": {}}
            except Exception as e:
                return {"success": False, "error": f"Failed to complete asset download: {e}", "data": {}}

class ReadPageTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="read_current_page",
            name="Web Page Reader",
            description="Reads and extracts unformatted, clean text contents from a target URL.",
            category="browser",
            tags=["browser", "read", "parse", "html", "scrape"],
            permission_level=0, # Level 0: Read-Only (Auto Allow)
            args_model=ReadPageArgs,
            usage_examples=["read_current_page(url='https://example.com')"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        url = kwargs.get("url", "")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=15.0)
                if response.status_code == 200:
                    html_content = response.text
                    clean_text = re.sub(r'<(script|style).*?>.*?</\1>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
                    clean_text = re.sub(r'<[^>]*?>', '', clean_text)
                    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                    
                    summary = clean_text[:2000] + "..." if len(clean_text) > 2000 else clean_text
                    return {"success": True, "data": {"content": summary}, "error": None}
                else:
                    return {"success": False, "error": f"Web server returned status code: {response.status_code}", "data": {}}
            except Exception as e:
                return {"success": False, "error": f"Failed to scrape web page: {e}", "data": {}}

# Import re for regex text cleaners
import re
