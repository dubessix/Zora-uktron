import React, { useState, useEffect } from 'react';
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
    system: { visible: false, x: 300, y: 220 }
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

  // Dispatch REST messages
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isProcessing) return;

    const userText = inputValue.trim();
    setInputValue("");
    setIsProcessing(true);
    setAiState("thinking");

    const localUserMsgId = "user_" + Date.now();
    setMessages(prev => [...prev, { id: localUserMsgId, sender: "user", text: userText }]);

    // NOTE: CONSTITUTIONAL COMPLIANCE (Rule 7, 8)
    // Removed all local client-side keyword-based widget toggling checks.
    // The backend's Structured AI Action is the sole trigger governing the UI.

    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          content: userText
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (!sessionId) {
          setSessionId(data.session_id);
        }
        
        // Append completion
        setMessages(prev => [...prev, {
          id: data.id,
          sender: "ai",
          text: data.content,
          personality: data.personality,
          response_ms: data.response_ms
        }]);
        
        // Set state to speaking, then return to idle
        setAiState("speaking");
        setTimeout(() => {
          setAiState("idle");
        }, 1200);

        // Intercept Structured AI Action (Constitution Rule 8)
        const structured = data.structured_action;
        if (structured && structured.action === "open_widget") {
          const targetWidgetId = structured.widget_id;
          setWidgetState(prev => ({
            ...prev,
            [targetWidgetId]: { ...prev[targetWidgetId], visible: true }
          }));
          addNotification(
            "AI Action Triggered", 
            `Ultron successfully analyzed your intent and deployed the matching ${targetWidgetId} workspace.`, 
            "medium"
          );
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
