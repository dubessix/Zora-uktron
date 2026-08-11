# Ultron V1: Frontend UI Project Structure & Backend Integration Manual
*Document Version: 1.0.0 — Ultimate Reference for UI Customization and LLM Feed*

This document provides a highly precise, technical, and exhaustive manual of the Ultron V1 React frontend directory structure and its precise API/WebSocket communication contracts.

Feed this exact document into any cloud AI (Claude, GPT, Gemini) to let it understand the exact interface boundaries, state variables, and event payloads needed to reconstruct, modify, or extend the Ultron V1 interface while keeping the backend entirely intact.

---

## 1. FRONTEND DIRECTORY TREE MAP

```
frontend/
├── package.json               # Main npm package dependencies (React 19, Vite, Tailwind CSS)
├── vite.config.js             # Vite compiler server configuration (Locked to Port 5173)
├── postcss.config.js          # PostCSS utility binder
├── tailwind.config.js         # Custom Tailwind theme colors, fonts, and breathing animations
├── index.html                 # Root entry viewport (links to main.jsx)
└── src/
    ├── main.jsx               # React entry point, mounts App.jsx
    ├── index.css              # Radial matte background gradient and SVG gooey canvas filter
    ├── App.jsx                # Core chat interface, keyboard shortcuts, and notification toast state
    ├── hooks/
    │   └── useDraggable.js    # Custom react hook tracking pointer coordinates and translate3d offsets
    └── components/
        ├── AppShell.jsx       # Global 3-panel widescreen grid layout with widget overlays
        ├── LeftPanel.jsx      # Telemetry meters column (omits legacy Vision Feed)
        ├── RightPanel.jsx     # Monospace chat dialogue bubbles and query text box
        ├── BlobCanvas.jsx     # Asynchronous Canvas 2D Particle Core with state-based breathing
        ├── NotificationToast.jsx # Floating glassmorphic notification toast with prioritized borders
        └── widgets/           # Glassmorphic floating components directory
            ├── WidgetContainer.jsx # Draggable container with double-click header collapse
            ├── WidgetManager.js   # Decoupled, OCP-compliant dynamic widget registry
            ├── TodoWidget.jsx      # Daily checklists (high/med/low)
            ├── CalendarWidget.jsx  # Chronological day schedule planner
            ├── GitWidget.jsx       # Active git repository status watcher (via backend git_status)
            ├── FileExplorerWidget.jsx # Connected local directory filesystem explorer (via backend file_read)
            ├── UniversalSearchWidget.jsx # Central unified search indexer (via backend)
            ├── DeepResearchWidget.jsx # Connected Tavily web searcher (via backend)
            ├── WeatherWidget.jsx   # Connected keyless Open-Meteo weather (via backend)
            ├── MarketWidget.jsx    # Stocks and crypto watchlist index (via backend)
            ├── TerminalWidget.jsx  # Terminal subprocess logs viewer (via backend)
            ├── MemoryWidget.jsx    # Vector SQLite memories viewer (via backend)
            ├── NotificationWidget.jsx # Background task completion alerts history
            └── SystemWidget.jsx    # psutil hardware metrics view (via backend system_metrics)
```

---

## 2. COMPONENT RESPONSIBILITIES & STATE MATRIX

When redesigning or customizing the UI, preserve these exact component interfaces:

### A. `App.jsx` (Global State Custodian)
Coordinates all WebSocket connections, active session parameters, and maps standard data flows:
*   `backendStatus`: `"CONNECTED"` | `"DISCONNECTED"` | `"ERROR"`. Checked via 5-second polling against `http://127.0.0.1:8000/api/health`.
*   `systemMetrics`: Object containing `{ memory_rss_mb, cpu_percent, total_system_ram_usage_percent }`.
*   `activePersonality`: `"ultron"` | `"zora"`. Governs visual asset color schemes and text prompt instructions.
*   `aiState`: `"idle"` | `"listening"` | `"thinking"` | `"planning"` | `"working"` | `"speaking"` | `"interrupted"` | `"background"`. Governs Canvas Core coordinates.
*   `notifications`: Array of active alerts `[{ id, title, message, priority }]`.
*   `widgetState`: Tracks visibility, positions, and coordinates for all 12 widgets:
    ```javascript
    const [widgetState, setWidgetState] = useState({
      todo: { visible: false, x: 120, y: 150 },
      calendar: { visible: false, x: 450, y: 120 },
      git: { visible: false, x: 220, y: 320 },
      file_explorer: { visible: false, x: 140, y: 180 },
      universal_search: { visible: false, x: 160, y: 220 },
      deep_research: { visible: false, x: 180, y: 240 },
      weather: { visible: false, x: 200, y: 120 },
      market: { visible: false, x: 220, y: 140 },
      terminal: { visible: false, x: 240, y: 160 },
      memory: { visible: false, x: 260, y: 180 },
      notification: { visible: false, x: 280, y: 200 },
      system: { visible: false, x: 300, y: 220 }
    });
    ```

### B. `AppShell.jsx` (3-Pane Grid Wrapper)
Renders a strict, widescreen layout dividing columns as follows:
*   **Column 1 (col-span-3)**: `<LeftPanel systemMetrics={systemMetrics} />`
*   **Column 2 (col-span-6)**: Center workspace housing `<BlobCanvas />` and the bottom-center control pill bar.
*   **Column 3 (col-span-3)**: `<RightPanel />` containing the monospace message bubble list.
*   **Draggable Overlays**: Dynamically loops over the active `widgetState` and renders open widgets wrapped inside `WidgetContainer` structures:
    ```javascript
    {Object.keys(widgetState).map(key => {
      const widget = widgetState[key];
      if (!widget.visible) return null;
      const config = WIDGET_REGISTRY[key];
      return (
        <WidgetContainer key={key} widgetId={key} title={config.title} onClose={() => toggleWidget(key)} ...>
          <config.Component />
        </WidgetContainer>
      );
    })}
    ```

### C. `BlobCanvas.jsx` (HTML5 Canvas 2D Core)
Renders 200 coordinate nodes forming a breathing particle sphere and concentric tilted orbital loops.
*   **Animation State Mapping**:
    *   `thinking`: Rotation speed: `0.025`, noise amplitude: `16.0`, scale: `1.08`.
    *   `listening` / `wake_word_detected`: Rotation: `0.001`, noise amplitude: `4.0 + amplitude * 18.0`, scale: `1.15`, orbital rings visible.
    *   `speaking`: Rotation: `0.006`, noise: `6.0 + Math.sin(time * 2.5) * 14.0` (follows speech rhythm), scale: `1.05`.
    *   `planning`: Rotation: `0.003`, orbital rings visible.
    *   `working`: Rotation: `0.012`, draws random network lines between adjacent nodes.
    *   `interrupted`: Rotation: `0.018`, noise: `22.0` (distortion wave), alpha: `0.35` (quick fade).
    *   `background` / `sleep`: Rotation: `0.0003`, noise: `0.8`, alpha: `0.22`.
*   **Visual Personalities**:
    *   *Ultron*: Cool cyan `#7DD3FC` and white particles.
    *   *Zora*: Warm purple `#C084FC` and pink-gold particles.

### D. `WidgetContainer.jsx` (Draggable Wrapper)
*   **useDraggable Hook**: Captures mouse movements on the header drag bar, updating hardware-accelerated CSS `transform: translate3d(x, y, 0)` variables directly to keep CPU utilization under 0.5%.
*   **Collapse State**: Double-clicking the header bar toggles `isCollapsed` state, hiding the inner children while keeping the header visible on screen.

---

## 3. UNIFIED FRONTEND-BACKEND INTEGRATION CONTRACTS

To ensure that your newly designed frontend communicates flawlessly with the backend Python services, use these exact REST and WebSocket specifications:

### A. Polling Health Contract
*   **Endpoint**: `GET http://127.0.0.1:8000/api/health`
*   **Response Payload**:
    ```json
    {
      "status": "healthy",
      "uptime_seconds": 124.52,
      "system_metrics": {
        "memory_rss_mb": 28.42,
        "cpu_percent": 0.0,
        "total_system_ram_usage_percent": 54.2
      },
      "environment": {
        "os_platform": "Linux",
        "os_release": "6.8.0-1008-aws",
        "python_version": "3.13.1"
      }
    }
    ```

### B. Dialogue completions Contract
*   **Endpoint**: `POST http://127.0.0.1:8000/api/chat`
*   **Request Payload**:
    ```json
    {
      "session_id": "your_session_uuid",  // String, optional
      "content": "Show downloads folder"   // String, required
    }
    ```
*   **Response Payload (Standard Completion)**:
    ```json
    {
      "id": "generated_message_uuid",
      "session_id": "active_session_uuid",
      "content": "Opening your local downloads directory...",
      "personality": "ultron",
      "response_ms": 14,
      "structured_action": {
        "action": "open_widget",
        "widget_id": "file_explorer"
      }
    }
    ```

### C. Direct Tool Execution Contract (Unified Tools API)
*   **Endpoint**: `POST http://127.0.0.1:8000/api/tools/execute`
*   **Request Payload**:
    ```json
    {
      "tool_id": "weather_tool",
      "arguments": {
        "latitude": 22.57,
        "longitude": 88.36
      },
      "has_confirmed": false
    }
    ```
*   **Response Payload (Standard ToolResult Model)**:
    ```json
    {
      "success": true,
      "data": {
        "location": "Lat: 22.57, Lon: 88.36",
        "temp": "28.0°C",
        "condition": "Scattered Clouds",
        "windspeed": "12 km/h",
        "hourly": [{"time": "02 PM", "temp": "29°C"}, {"time": "05 PM", "temp": "27°C"}],
        "weekly": [{"day": "MON", "temp": "28°C", "cond": "Cloudy"}]
      },
      "error": null,
      "metadata": {
        "execution_time_ms": 142,
        "tool_name": "Weather Watcher"
      }
    }
    ```
*   **Response Payload (Confirmation Gate Intercept)**:
    If the requested tool requires manual confirmation (Level 2 or 3) and `has_confirmed=false` is passed:
    ```json
    {
      "status": "PENDING_CONFIRMATION",
      "tool_id": "terminal_run",
      "message": "Tool 'terminal_run' requires manual confirmation for execution.",
      "required_permission_level": 2
    }
    ```

---

## 4. CONSTITUTIONAL COMPLIANCE (Rule 7, 8)
When rebuilding the UI, you must **never hardcode keyword-based widget toggling checks on the client side**. 
*   **The Law**: The backend's returned **`structured_action`** payload is the sole authority governing the UI.
*   **The Client-Side Interceptor Flow**:
    When a completion is received:
    1.  Parse `data.structured_action`.
    2.  If `structured_action.action === "open_widget"`, extract `structured_action.widget_id`.
    3.  Set `widgetState[widget_id].visible = true` dynamically inside your React state.
    4.  The `WidgetManager` will automatically mount and render the widget on-screen.
