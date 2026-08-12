import React, { useState } from 'react';
import LeftPanel from './LeftPanel';
import RightPanel from './RightPanel';
import BlobCanvas from './BlobCanvas';
import useVoice from '../hooks/useVoice';

// Import dynamic widget registry structures (Requirement: Never hardcode widgets in AppShell)
import { WIDGET_REGISTRY } from './widgets/WidgetManager';
import WidgetContainer from './widgets/WidgetContainer';

/**
 * AppShell Component
 * Implements the responsive 3-panel widescreen dashboard layout.
 * Houses left system stats, center canvas particle core, right chat dialogues,
 * and dynamically iterates over the WIDGET_REGISTRY to render open draggable widgets.
 * The IRIS header name + accent color switch dynamically between Ultron (emerald)
 * and Zora (pink). The bottom mic toggles browser-native wake-word listening.
 */
export default function AppShell({ 
  messages, 
  inputValue, 
  setInputValue, 
  handleSendMessage, 
  isProcessing, 
  activePersonality, 
  systemMetrics,
  aiState,
  setAiState,
  togglePersonality,
  widgetState,
  toggleWidget,
  handleVoiceCommand,
  codingMode,
  toggleCodingMode,
  codingLog
}) {
  const isZora = activePersonality === "zora";
  const accent = isZora ? "#EC4899" : "#10B981"; // pink vs emerald
  const accentText = isZora ? "text-pink-400" : "text-emerald-400";
  const accentRing = isZora ? "border-pink-400/30" : "border-emerald-400/30";
  const accentBg = isZora ? "bg-pink-500/10" : "bg-emerald-500/10";
  const accentDot = isZora ? "bg-pink-400" : "bg-emerald-400";
  const aiName = isZora ? "Zora" : "Ultron";

  // Voice control: wake-word listening wired to the bottom mic toggle.
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const voice = useVoice({
    enabled: voiceEnabled,
    onCommand: (cmd) => {
      if (handleVoiceCommand) handleVoiceCommand(cmd);
    }
  });

  const handleMicToggle = () => {
    setVoiceEnabled((prev) => !prev);
  };

  return (
    <div className="flex flex-col h-screen w-screen p-6 select-none bg-transparent overflow-hidden text-[#F5F5F7] relative">
      
      {/* ==============================================================================
          1. SYSTEM HEADER & TOP NAVIGATION (Dynamic IRIS identity)
         ============================================================================== */}
      <header className="flex justify-between items-center border-b border-white/5 pb-4 mb-6 z-10 font-mono">
        <div className="flex items-center gap-2">
          <span className={`text-2xl font-black italic tracking-tight uppercase transition-all duration-500 drop-shadow-[0_0_12px_rgba(16,185,129,0.35)] ${isZora ? "text-pink-400" : "text-emerald-400"}`}
            style={{ fontFamily: "'Arial Black', 'Segoe UI', system-ui, sans-serif", textShadow: isZora ? "0 0 18px rgba(236,72,153,0.55)" : "0 0 18px rgba(16,185,129,0.55)" }}>
            {aiName}
          </span>
        </div>

        {/* Minimal status capsule — no clutter */}
        <div className={`flex items-center gap-1.5 text-[8px] px-2 py-1.5 rounded-full border backdrop-blur-3xl ${accentRing} ${accentBg}`}>
          <div className={`w-1.5 h-1.5 ${accentDot} rounded-full animate-pulse`} />
          <span className={`font-bold tracking-widest uppercase ${accentText}`}>
            {isZora ? "Zora Online" : "Ultron Online"}
          </span>
        </div>
      </header>

      {/* 2. THREE-PANEL CORE GRID WORKSPACE */}
      <div className="flex-1 grid grid-cols-12 gap-6 items-stretch overflow-hidden z-10">
        
        {/* Left column: Relational resource meters */}
        <LeftPanel systemMetrics={systemMetrics} />

        {/* Center column: HTML5 Canvas particle loop & concentric orbital rings */}
        <main className="col-span-12 lg:col-span-6 flex flex-col items-center justify-center relative bg-white/[0.01] border border-white/5 rounded-sm p-6 backdrop-blur-xl">
          
          {/* Header context indicators */}
          <div className="absolute top-6 left-6 font-mono text-[9px] text-[#8B8B96] flex items-center gap-2">
            <span>CORE STATUS:</span>
            <span className={`uppercase tracking-wider font-bold ${voice.wakeDetected ? "text-pink-400" : "text-[#7DD3FC]"}`}>
              {voice.wakeDetected ? "WAKED" : aiState}
            </span>
          </div>

          {/* Quick-toggle widget hot-buttons inside center pane */}
          <div className="absolute top-6 right-6 flex gap-2">
            {Object.keys(WIDGET_REGISTRY).map(key => {
              const config = WIDGET_REGISTRY[key];
              const isVisible = widgetState[key]?.visible;
              return (
                <button 
                  key={key}
                  onClick={() => toggleWidget(key)}
                  className={`px-2 py-0.5 border text-[8px] font-mono rounded-sm transition-all uppercase ${
                    isVisible ? "border-[#7DD3FC]/40 text-[#7DD3FC] bg-[#7DD3FC]/5" : "border-white/5 text-white/30"
                  }`}
                >
                  {config.id}
                </button>
              );
            })}
          </div>

          {/* Core Canvas particle loop component */}
          <div className="flex-1 flex items-center justify-center">
            <BlobCanvas 
              aiState={voice.wakeDetected ? "wake_word_detected" : (voice.isListening ? "listening" : aiState)} 
              personality={activePersonality} 
              amplitude={0.0}
            />
          </div>

          {/* Center Bottom floating pill control bar */}
          <div className="absolute bottom-6 flex items-center gap-3 bg-white/[0.02] border border-white/5 px-4 py-2 rounded-full backdrop-blur-3xl font-mono text-[9px]">
            {/* Camera icon */}
            <button className="text-white/20 hover:text-white/50 transition-colors px-2">
              📷
            </button>

            {/* Red crossed status indicator from mockup */}
            <div className="w-5 h-5 rounded-full bg-rose-500/20 border border-rose-500/30 flex items-center justify-center text-[8px] text-rose-400">
              ✖
            </div>
            
            {/* Status pill button - switches personality on click */}
            <button 
              onClick={togglePersonality}
              className={`px-3 py-1 rounded-full text-[8px] font-bold tracking-widest uppercase transition-all duration-500 border ${
                isZora
                  ? "bg-pink-500/10 border-pink-400/20 text-pink-300 shadow-[0_0_15px_rgba(236,72,153,0.15)]"
                  : "bg-emerald-500/10 border-emerald-400/20 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.15)]"
              }`}
            >
              {isZora ? "Zora Online" : "Ultron Online"}
            </button>

            {/* Coding Mode toggle — NVIDIA coding brain */}
            <button 
              onClick={toggleCodingMode}
              className={`px-3 py-1 rounded-full text-[8px] font-bold tracking-widest uppercase transition-all duration-500 border ${
                codingMode
                  ? "bg-sky-500/10 border-sky-400/30 text-sky-300 shadow-[0_0_15px_rgba(56,189,248,0.2)]"
                  : "border-white/10 text-white/30 hover:text-white/60"
              }`}
              title={codingMode ? "Coding Mode ON (NVIDIA brain for all turns). Click to revert to auto." : "Coding Mode OFF (auto-detect). Click to force NVIDIA coding brain."}
            >
              💻 {codingMode ? "Coding ON" : "Coding"}
            </button>

            {/* Mic icon — real wake-word listening toggle with pulse-ring effect */}
            <button 
              onClick={handleMicToggle}
              className={`relative flex items-center justify-center w-8 h-8 rounded-full border transition-all duration-500 ${
                voice.isListening
                  ? isZora
                    ? "text-pink-400 border-pink-400/40 bg-pink-500/10"
                    : "text-emerald-400 border-emerald-400/40 bg-emerald-500/10"
                  : "text-white/20 border-white/10 hover:text-white/60 hover:border-white/20"
              }`}
              title={voice.isListening ? "Listening for wake word... (click to stop)" : "Enable voice (click to start listening)"}
            >
              <span className={`text-sm ${voice.isListening ? "animate-pulse" : ""}`}>🎙️</span>
              {voice.isListening && (
                <span className={`absolute inset-0 rounded-full animate-ping opacity-40 ${isZora ? "bg-pink-400/40" : "bg-emerald-400/40"}`} />
              )}
            </button>
          </div>

          {/* Voice listening hint */}
          {voice.isListening && (
            <div className="absolute bottom-6 right-6 text-[8px] font-mono uppercase tracking-widest text-pink-300/80">
              {voice.wakeDetected ? "Wake word heard — speak your command..." : "Listening for wake word..."}
            </div>
          )}

        </main>

        {/* Right column: Monospace dialogue history and textbox */}
        <RightPanel 
          messages={messages}
          inputValue={inputValue}
          setInputValue={setInputValue}
          handleSendMessage={handleSendMessage}
          isProcessing={isProcessing}
          activePersonality={activePersonality}
        />

      </div>

      {/* ==============================================================================
          3. DYNAMIC FLOATING OVERLAYS (Requirement: Loop over WIDGET_REGISTRY - No Hardcoding)
         ============================================================================== */}
      
      {Object.keys(widgetState).map(key => {
        const widget = widgetState[key];
        if (!widget.visible) return null;
        
        const config = WIDGET_REGISTRY[key];
        if (!config) return null;
        
        return (
          <WidgetContainer 
            key={key}
            widgetId={key}
            title={config.title} 
            onClose={() => toggleWidget(key)}
            initialX={widget.x}
            initialY={widget.y}
            initialWidth={config.defaultWidth}
            initialHeight={config.defaultHeight}
            personality={activePersonality}
          >
            <React.Suspense fallback={
              <div className="p-4 text-[9px] font-mono text-white/40 uppercase tracking-widest flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-[#7DD3FC] rounded-full animate-ping" />
                Lazy loading assets...
              </div>
            }>
              {key === "coding" ? (
                <config.Component log={codingLog || []} />
              ) : (
                <config.Component />
              )}
            </React.Suspense>
          </WidgetContainer>
        );
      })}

    </div>
  );
}

