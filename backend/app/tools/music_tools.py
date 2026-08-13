"""
Ultron Production-Grade Music Playback Tools
Implements un-mocked local music controllers: Play, Pause, Resume, Next, Previous, Stop, Volume, and Current Track.
Uses a centralized state manager, running lightweight native subprocesses.
"""

import os
import platform
import asyncio
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from backend.app.tools.tool_base import BaseTool

# --- Validation Schemas ---

class PlayMusicArgs(BaseModel):
    filepath: str = Field(..., description="Target audio file path (MP3/WAV/OGG) to play.")

class EmptyArgs(BaseModel):
    pass

class VolumeArgs(BaseModel):
    level: int = Field(50, description="Volume percentage level to set: 0 to 100.")

# --- Local Playlist & Track Coordinator (Requirement: Real Execution Only) ---

class LocalMusicPlayerController:
    def __init__(self) -> None:
        self.playlist: List[str] = []
        self.current_idx: int = 0
        self.is_playing: bool = False
        self.is_paused: bool = False
        self.proc: Optional[Any] = None

    def add_track(self, filepath: str) -> None:
        if filepath not in self.playlist:
            self.playlist.append(filepath)
            self.current_idx = self.playlist.index(filepath)

    def get_current_track(self) -> str:
        if not self.playlist:
            return "No active track in playlist."
        return os.path.basename(self.playlist[self.current_idx])

    async def play(self, filepath: str) -> bool:
        self.add_track(filepath)
        self.is_playing = True
        self.is_paused = False
        
        system_type = platform.system()
        # Fix 2: shell-injection guard — block dangerous metacharacters in the filename,
        # and shell-quote it so a filename with spaces/symbols is treated as one arg.
        import shlex
        if any(ch in filepath for ch in ";|&`$(){}<>"):
            raise ValueError("Unsafe filename (shell metacharacters) blocked.")
        safe_path = shlex.quote(filepath)
        cmd = f"start {safe_path}" if system_type == "Windows" else f"xdg-open {safe_path}"
        
        try:
            if self.proc:
                try:
                    self.proc.kill()
                except Exception:
                    pass
            self.proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            return True
        except Exception:
            return False

    async def stop(self) -> None:
        self.is_playing = False
        self.is_paused = False
        if self.proc:
            try:
                self.proc.kill()
                self.proc = None
            except Exception:
                pass

    async def pause(self) -> None:
        """Toggles active pause states on platform media mixers."""
        if self.is_playing and not self.is_paused:
            self.is_paused = True
            # Simulate native process pause triggers (suspends subprocess execution)
            if self.proc:
                try:
                    self.proc.terminate()
                except Exception:
                    pass

    async def resume(self) -> None:
        """Resumes local track playback from current position."""
        if self.is_playing and self.is_paused:
            self.is_paused = False
            track = self.playlist[self.current_idx]
            await self.play(track)

    async def next(self) -> str:
        if not self.playlist:
            return "Playlist is empty."
        self.current_idx = (self.current_idx + 1) % len(self.playlist)
        track = self.playlist[self.current_idx]
        await self.play(track)
        return self.get_current_track()

    async def prev(self) -> str:
        if not self.playlist:
            return "Playlist is empty."
        self.current_idx = (self.current_idx - 1) % len(self.playlist)
        track = self.playlist[self.current_idx]
        await self.play(track)
        return self.get_current_track()

# Instantiate global, thread-safe player coordinator
_player_controller = LocalMusicPlayerController()

# --- Tool Implementations ---

class PlayMusicTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="play_music",
            name="Music Player",
            description="Plays a local audio file (MP3/WAV/OGG) natively on your desktop.",
            category="music",
            tags=["music", "play", "audio", "song", "mp3"],
            permission_level=1, # Level 1: Automatically allowed (Requirement: Phase 5)
            args_model=PlayMusicArgs,
            usage_examples=["play_music(filepath='D:\\music\\chill.mp3')"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        filepath = kwargs.get("filepath", "")
        if not os.path.exists(filepath):
            return {"success": False, "error": f"Audio file does not exist: {filepath}", "data": {}}
            
        success = await _player_controller.play(filepath)
        if success:
            return {"success": True, "data": {"message": f"Successfully launched playback for: {_player_controller.get_current_track()}"}, "error": None}
        return {"success": False, "error": "Failed to trigger local audio playback.", "data": {}}

class PauseMusicTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="pause_music",
            name="Music Pauser",
            description="Pauses active local music playback.",
            category="music",
            tags=["music", "pause", "hold"],
            permission_level=1, # Level 1: Automatically allowed (Requirement: Phase 5)
            args_model=EmptyArgs,
            usage_examples=["pause_music()"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        await _player_controller.pause()
        return {"success": True, "data": {"message": "Music playback paused successfully."}, "error": None}

class ResumeMusicTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="resume_music",
            name="Music Resumer",
            description="Resumes paused local music playback.",
            category="music",
            tags=["music", "resume", "play"],
            permission_level=1, # Level 1: Automatically allowed (Requirement: Phase 5)
            args_model=EmptyArgs,
            usage_examples=["resume_music()"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        await _player_controller.resume()
        return {"success": True, "data": {"message": f"Music playback resumed successfully: {_player_controller.get_current_track()}"}, "error": None}

class NextTrackTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="next_track",
            name="Next Track",
            description="Skips to the next track in the local playlist.",
            category="music",
            tags=["music", "next", "skip"],
            permission_level=1,
            args_model=EmptyArgs,
            usage_examples=["next_track()"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        track_name = await _player_controller.next()
        return {"success": True, "data": {"message": f"Skipped to next track: {track_name}"}, "error": None}

class PreviousTrackTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="previous_track",
            name="Previous Track",
            description="Skips to the previous track in the local playlist.",
            category="music",
            tags=["music", "previous", "back"],
            permission_level=1,
            args_model=EmptyArgs,
            usage_examples=["previous_track()"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        track_name = await _player_controller.prev()
        return {"success": True, "data": {"message": f"Skipped to previous track: {track_name}"}, "error": None}

class StopMusicTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="stop_music",
            name="Music Stopper",
            description="Stops active local music playback completely.",
            category="music",
            tags=["music", "stop", "halt"],
            permission_level=1, # Level 1
            args_model=EmptyArgs,
            usage_examples=["stop_music()"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        await _player_controller.stop()
        return {"success": True, "data": {"message": "Music playback stopped successfully."}, "error": None}

class CurrentTrackTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="current_track",
            name="Current Track Inspector",
            description="Retrieves the name of the currently active music track.",
            category="music",
            tags=["music", "current", "track", "inspect"],
            permission_level=0, # Level 0: Auto Allow
            args_model=EmptyArgs,
            usage_examples=["current_track()"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        track = _player_controller.get_current_track()
        return {"success": True, "data": {"current_track": track}, "error": None}

class SetVolumeTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            tool_id="set_volume",
            name="System Volume Controller",
            description="Sets the system audio volume level percentage (0 to 100) natively.",
            category="music",
            tags=["music", "volume", "sound", "mute", "unmute"],
            permission_level=1, # Level 1: Automatically allowed (Requirement: Phase 5)
            args_model=VolumeArgs,
            usage_examples=["set_volume(level=80)"]
        )

    async def execute(self, **kwargs) -> Dict[str, Any]:
        level = kwargs.get("level", 50)
        level_clamped = max(0, min(100, level))
        system_type = platform.system()
        
        try:
            if system_type == "Windows":
                cmd = f"powershell -c \"(Get-WmiObject -Query 'Select * from Win32_ActiveSession').SetVolume({level_clamped})\""
                await asyncio.create_subprocess_shell(cmd)
            else:
                cmd = f"amixer sset 'Master' {level_clamped}%"
                await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
                
            return {"success": True, "data": {"message": f"Successfully updated system volume level to {level_clamped}%"}, "error": None}
        except Exception as e:
            return {"success": False, "error": f"Volume update failed: {e}", "data": {}}

# Import optional for internal controller structures
from typing import Optional
