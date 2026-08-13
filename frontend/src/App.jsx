import React, { useState, useEffect, useRef } from 'react';
import AppShell from './components/AppShell';
import NotificationToast from './components/NotificationToast';

/**
 * Ultron Web Client Root App
 * Coordinates websocket connections, local state parameters, and maps
 * standard data flows, notification toast systems, and keyboard fallbacks.
 * Dynamically launches and positions 12 distinct widgets.
 */
export default function App() {
  const [backendStatus, setBackendStatus] = useState("DISCONNECTED");
  const [systemMetrics, setSystemMetrics] = useState(null);
  
  const [sessionId, setSessionId] = useState(null);
  const [activePersonality, setActivePersonality] = useState("ultron");
  const [aiState, setAiState] = useState("idle");
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  // Coding Mode (NVIDIA brain) — manual toggle synced to backend /api/coding-mode
  const [codingMode, setCodingMode] = useState(false);
  // Coding activity log shown in the CodingWidget; auto-opened on coding turns.
  const [codingLog, setCodingLog] = useState([]);
  // P0-3: track a pending dangerous action so the user can confirm & run it.
  const [pendingConfirm, setPendingConfirm] = useState(false);
  // Real-time operational log (Log tab)
  const [logs, setLogs] = useState([]);
  const [lastUserText, setLastUserText] = useState("");

  // Widget floating toggle states (Requirement: Remember coordinates & state)
  const [widgetState, setWidgetState] = useState({
    todo: { visible: false, x: 120, y: 150 },
    calendar: { visible: false, x: 450, y: 120 },
    reminder: { visible: false, x: 320, y: 140 },
    code_optimizer: { visible: false, x: 340, y: 160 },
    semantic_code_graph: { visible: false, x: 360, y: 180 },
    security_guardian: { visible: false, x: 380, y: 200 },
    daily_briefing: { visible: false, x: 400, y: 220 },
    git: { visible: false, x: 220, y: 320 },
    file_explorer: { visible: false, x: 140, y: 180 },
    universal_search: { visible: false, x: 160, y: 220 },
    deep_research: { visible: false, x: 180, y: 240 },
    weather: { visible: false, x: 200, y: 120 },
    market: { visible: false, x: 220, y: 140 },
    terminal: { visible: false, x: 240, y: 160 },
    memory: { visible: false, x: 260, y: 180 },
    notification: { visible: false, x: 280, y: 200 },
    system: { visible: false, x: 300, y: 220 },
    coding: { visible: false, x: 360, y: 300 },
    music: { visible: false, x: 380, y: 320 },
    world_monitor: { visible: false, x: 400, y: 340 },
    github_search: { visible: false, x: 420, y: 360 }
  });

  // Dynamic Notification Toasts Queue (Requirement: Notification Prioritization)
  const [notifications, setNotifications] = useState([]);

  // Add a new notification toast
  const addNotification = (title, message, priority = "low") => {
    const newId = "notif_" + Date.now() + "_" + Math.random().toString(36).substr(2, 5);
    setNotifications(prev => [...prev, { id: newId, title, message, priority }]);
  };

  // Dismiss an active notification toast
  const dismissNotification = (id) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  };

  // Keyboard Shortcuts (Requirement: Optional Fallback Controls)
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Toggle widgets on Ctrl+Alt key bounds
      if (e.ctrlKey && e.altKey) {
        if (e.key.toLowerCase() === 't') {
          toggleWidget('todo');
        } else if (e.key.toLowerCase() === 'c') {
          toggleWidget('calendar');
        } else if (e.key.toLowerCase() === 'g') {
          toggleWidget('git');
        }
      }
      // Escape closes all open widgets instantly (Clean workspace helper)
      if (e.key === 'Escape') {
        setWidgetState(prev => {
          const reset = {};
          Object.keys(prev).forEach(key => {
            reset[key] = { ...prev[key], visible: false };
          });
          return reset;
        });
        addNotification("Workspace Cleaned", "All floating widgets have been collapsed.", "low");
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Poll backend health and system metrics
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
        const response = await fetch(`${apiUrl}/api/health`);
        if (response.ok) {
          const data = await response.json();
          setBackendStatus("CONNECTED");
          setSystemMetrics(data.system_metrics);
        } else {
          setBackendStatus("ERROR");
        }
      } catch (err) {
        setBackendStatus("DISCONNECTED");
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  // Handle active personality toggling (smooth handoff)
  const togglePersonality = () => {
    const nextPers = activePersonality === "ultron" ? "zora" : "ultron";
    setActivePersonality(nextPers);
    setAiState("planning"); // Transition state pulse
    setTimeout(() => {
      setAiState("idle");
    }, 1000);
  };

  // Toggle Coding Mode (manual override -> NVIDIA brain for all turns)
  const toggleCodingMode = async () => {
    const next = !codingMode;
    setCodingMode(next);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${apiUrl}/api/coding-mode`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled: next })
      });
      if (!response.ok) {
        // rollback on failure
        setCodingMode(!next);
        addNotification("Coding Mode", "Failed to toggle coding mode.", "medium");
      }
    } catch (err) {
      setCodingMode(!next);
      addNotification("Coding Mode", "Backend offline — coding mode not changed.", "medium");
    }
  };

  // Handle a coding response: auto-open the coding panel + log it (so the user
  // doesn't have to go click a button — it follows the conversation).
  const handleCodingResponse = (data) => {
    if (!data.coding) return;
    const short = (data.content || "").slice(0, 220);
    setCodingLog(prev => [...prev.slice(-19), short]);
    setWidgetState(prev => ({
      ...prev,
      coding: { ...prev.coding, visible: true }
    }));
  };

  // P0-3: confirm & re-run the last pending dangerous action.
  const handleConfirmRun = async () => {
    if (!lastUserText || isProcessing) return;
    setPendingConfirm(true);
    // Re-send the last command with has_confirmed=true via the existing handler.
    setInputValue(lastUserText);
    await new Promise(r => setTimeout(r, 0));
    // trigger send with confirm flag
    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, content: lastUserText, has_confirmed: true })
      });
      if (response.ok) {
        const data = await response.json();
        if (!sessionId) setSessionId(data.session_id);
        setMessages(prev => [...prev, { id: data.id, sender: "ai", text: data.content, personality: data.personality, response_ms: data.response_ms }]);
      }
    } catch (err) { /* ignore */ } finally {
      setPendingConfirm(false);
    }
  };

  // P1: speak the AI response aloud via /api/speak (real TTS).
  const speakResponse = async (text, personality = "ultron") => {
    if (!text || text.startsWith("[Mock")) return; // skip mock/debug lines
    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${apiUrl}/api/speak`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, personality })
      });
      if (!res.ok) return;
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      await audio.play().catch(() => {});
      audio.onended = () => URL.revokeObjectURL(url);
    } catch (err) { /* silent */ }
  };

  // Toggle individual widget visibility
  const toggleWidget = (widgetId) => {
    setWidgetState(prev => ({
      ...prev,
      [widgetId]: {
        ...prev[widgetId],
        visible: !prev[widgetId].visible
      }
    }));
  };

  // Submit a command directly (used by wake-word voice input)
  const handleVoiceCommand = async (text) => {
    if (!text.trim() || isProcessing) return;
    const userText = text.trim();
    setInputValue("");
    setIsProcessing(true);
    setAiState("thinking");

    const localUserMsgId = "user_" + Date.now();
    setMessages(prev => [...prev, { id: localUserMsgId, sender: "user", text: userText }]);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, content: userText })
      });

      if (response.ok) {
        const data = await response.json();
        if (!sessionId) setSessionId(data.session_id);
        setMessages(prev => [...prev, {
          id: data.id,
          sender: "ai",
          text: data.content,
          personality: data.personality,
          response_ms: data.response_ms
        }]);
        setAiState("speaking");
        speakResponse(data.content, data.personality || "ultron");
        setTimeout(() => setAiState("idle"), 1200);
        const structured = data.structured_action;
        if (structured && structured.action === "open_widget") {
          const targetWidgetId = structured.widget_id;
          setWidgetState(prev => ({
            ...prev,
            [targetWidgetId]: { ...prev[targetWidgetId], visible: true }
          }));
        }
        handleCodingResponse(data);
      } else {
        setMessages(prev => [...prev, {
          id: "error_" + Date.now(), sender: "system_error",
          text: "System communication error."
        }]);
        setAiState("idle");
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        id: "error_" + Date.now(), sender: "system_error",
        text: "Dropped. Backend server is offline."
      }]);
      setAiState("idle");
    } finally {
      setIsProcessing(false);
    }
  };

  // Dispatch REST messages
  // C-1: real WebSocket streaming for chat (Jarvis-style token-by-token).
  const wsRef = useRef(null);
  const sendViaWS = (text) => {
    return new Promise((resolve) => {
      const apiUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
      const wsBase = apiUrl.replace(/^http/, "ws");
      let ws;
      try {
        ws = new WebSocket(`${wsBase}/ws/chat?client_id=web`);
      } catch (e) { resolve(null); return; }
      wsRef.current = ws;
      let acc = "";
      ws.onopen = () => ws.send(JSON.stringify({ content: text, session_id: sessionId || "" }));
      ws.onmessage = (ev) => {
        let msg; try { msg = JSON.parse(ev.data); } catch { return; }
        if (msg.type === "progress") return;
        if (msg.type === "token") { acc += msg.content; }
        else if (msg.type === "done") {
          const data = { id: msg.message_id, content: acc, personality: msg.active_personality, response_ms: msg.response_ms, coding: msg.coding, intent: msg.intent, events: msg.events || [] };
          try { ws.close(); } catch {}
          wsRef.current = null;
          resolve(data);
        }
      };
      ws.onerror = () => { try { ws.close(); } catch {} wsRef.current = null; resolve(null); };
    });
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isProcessing) return;

    const userText = inputValue.trim();
    setInputValue("");
    setLastUserText(userText);
    setIsProcessing(true);
    setAiState("thinking");

    const localUserMsgId = "user_" + Date.now();
    setMessages(prev => [...prev, { id: localUserMsgId, sender: "user", text: userText }]);

    // NOTE: CONSTITUTIONAL COMPLIANCE (Rule 7, 8)
    // Removed all local client-side keyword-based widget toggling checks.
    // The backend's Structured AI Action is the sole trigger governing the UI.

    try {
      // C-1: stream via WebSocket for real token-by-token typing.
      const data = await sendViaWS(userText);
      if (data) {
        if (!sessionId) setSessionId("web_" + Date.now());
        
        setMessages(prev => [...prev, {
          id: data.id || ("ai_" + Date.now()),
          sender: "ai",
          text: data.content || "",
          personality: data.personality || "ultron",
          response_ms: data.response_ms
        }]);
        
        setAiState("speaking");
        speakResponse(data.content, data.personality || "ultron");
        setTimeout(() => setAiState("idle"), 1200);
        handleCodingResponse(data);
        // Log tab: collect real-time tool/activity events
        if (data.events && data.events.length) {
          const logLines = data.events.filter(e => e.type === "log").map(e => ({ level: e.log.level, message: e.log.message }));
          if (logLines.length) setLogs(prev => [...prev, ...logLines].slice(-80));
        }
      } else {
        setMessages(prev => [...prev, {
          id: "error_" + Date.now(),
          sender: "system_error",
          text: "System communication error."
        }]);
        setAiState("idle");
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        id: "error_" + Date.now(),
        sender: "system_error",
        text: "Dropped. Backend server is offline."
      }]);
      setAiState("idle");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="relative h-screen w-screen overflow-hidden bg-transparent">
      {/* 3-Panel Main Widescreen Layout */}
      <AppShell 
        messages={messages}
        inputValue={inputValue}
        setInputValue={setInputValue}
        handleSendMessage={handleSendMessage}
        isProcessing={isProcessing}
        activePersonality={activePersonality}
        systemMetrics={systemMetrics}
        aiState={aiState}
        setAiState={setAiState}
        togglePersonality={togglePersonality}
        widgetState={widgetState}
        toggleWidget={toggleWidget}
        handleVoiceCommand={handleVoiceCommand}
        codingMode={codingMode}
        toggleCodingMode={toggleCodingMode}
        codingLog={codingLog}
        onConfirmRun={handleConfirmRun}
        logs={logs}
      />

      {/* ==============================================================================
          4. FLOATING NOTIFICATION TOAST OVERLAYS (Requirement: Notification Prioritization)
         ============================================================================== */}
      <div className="absolute top-6 right-6 z-[1000] flex flex-col gap-3 pointer-events-none font-mono">
        {notifications.map(notif => (
          <div key={notif.id} className="pointer-events-auto animate-slide-in">
            <NotificationToast 
              id={notif.id}
              title={notif.title}
              message={notif.message}
              priority={notif.priority}
              onDismiss={dismissNotification}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
