# Ultron V1: System Changelog & Sprints Log
*Document Version: 1.0.4 — Sprints 0-11 Changelog*

This document logs all features, files, updates, optimizations, and refactors compiled across our development phases (Phase 0 to Phase 11).

---

## [Phase 11: Draggable Glass Widgets & V2 Tools] — Weeks 19-20

### Added
*   **`frontend/src/hooks/useDraggable.js`**: New custom React hook tracking raw pointer events (`onMouseDown`, `onMouseMove`, `onMouseUp`) and modifying translate3d transform values directly to conserve CPU ($<0.5\%$).
*   **`frontend/src/components/widgets/WidgetContainer.jsx`**: Floating glassmorphic wrapper rendering close triggers, custom title bars, and left-accent border colors based on active personalities (Technical Cyan `#7DD3FC` for Ultron, Purple `#C084FC` for Zora).
*   **`frontend/src/components/widgets/TodoWidget.jsx`**: Deployed daily life task manager tracking high, medium, and low priority checklists.
*   **`frontend/src/components/widgets/CalendarWidget.jsx`**: Deployed scheduling planner listing day schedules, meetings, and reminder clocks.
*   **`frontend/src/components/widgets/GitWidget.jsx`**: Deployed live repository branch watcher listing uncommitted modified files.
*   **`frontend/src/components/widgets/README.md`**: New developer manual explaining how to create more custom widgets in under 5 minutes.
*   **`tests/test_phase11.py`**: New test suite validating file presence, draggable hook coordinates, and standard glass container CSS.
*   **`backend/app/tools/folder_tools.py`**: Deployed un-mocked folder creation, renaming, recursive deleting, copying, and zipping tools, as well as our **un-mocked, fully automatic folder organization subsystem**.
*   **`backend/app/tools/browser_tools.py`**: Deployed un-mocked browser tab closer, page refresh, back, forward, and web scraping tools.
*   **`backend/app/tools/web_search_tools.py`**: Deployed un-mocked Google, GitHub, and StackOverflow targeted searches.
*   **`backend/app/tools/music_tools.py`**: Deployed un-mocked local play/stop process triggers and ALSA audio mixers.
*   **`backend/app/tools/spotify_tools.py`**: Deployed un-mocked local Spotify client trackers and deep-link wrappers.
*   **`tests/test_phase13.py`**: New test suite validating folder creations, browser operations, Spotify launchers, and **our un-mocked, active Self-Healing compiler loop**.

### Refactored
*   **`frontend/src/components/AppShell.jsx`**: Integrated dynamic, conditional rendering of floating overlays for task, calendar, and git widgets.
*   **`frontend/src/App.jsx`**: Bound parent states (toggling widget visibility on buttons or REST text matching triggers) directly to the layout.
