import React from 'react';
import LeftPanel from './LeftPanel';
import RightPanel from './RightPanel';
import BlobCanvas from './BlobCanvas';

// Import dynamic widget registry structures (Requirement: Never hardcode widgets in AppShell)
import { WIDGET_REGISTRY } from './widgets/WidgetManager';
import WidgetContainer from './widgets/WidgetContainer';

/**
 * AppShell Component
 * Implements the responsive 3-panel widescreen dashboard layout.
 * Houses left system stats, center canvas particle core, right chat dialogues,
 * and dynamically iterates over the WIDGET_REGISTRY to render open draggable widgets.
 * Integrates the top navigation capsule bar exactly as shown in the mockup.
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
  toggleWidget
}) {
  return (
    <div className="flex flex-col h-screen w-screen p-6 select-none bg-transparent overflow-hidden text-[#F5F5F7] relative">
      
      {/* ==============================================================================
          1. SYSTEM HEADER & TOP NAVIGATION CAPSULE BAR (Mockup Header)
         ============================================================================== */}
      <header className="flex justify-between items-center border-b border-white/5 pb-4 mb-6 z-10 font-mono">
        <div className="flex items-center gap-2">
          {/* Glowing Eye Icon from mockup */}
          <div className="text-emerald-400 text-sm">👁️</div>
          <span className="text-xs font-bold tracking-widest text-[#F5F5F7] uppercase">
            IRIS AI // ULTRON V1
          </span>
        </div>

        {/* Center Top Capsule Navbar */}
        <div className="flex items-center gap-1.5 bg-white/[0.02] border border-white/5 px-2 py-1.5 rounded-full backdrop-blur-3xl text-[8px] font-bold tracking-widest uppercase">
          <button className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-full">
            Command
          </button>
          <button className="px-3 py-1 hover:text-white transition-colors">
            Notes
          </button>
          <button className="px-3 py-1 hover:text-white transition-colors">
            Gallery
          </button>
          <button className="px-3 py-1 hover:text-white transition-colors">
            Mobile
          </button>
          <button className="px-3 py-1 hover:text-white transition-colors">
            Settings
          </button>
        </div>

        <div className="flex items-center gap-1.5 text-[8px]">
          <span className="text-white/20">NETWORK:</span>
          <span className="text-emerald-400 font-bold tracking-widest uppercase flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse" />
            Connected
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
            <span className="text-[#7DD3FC] uppercase tracking-wider font-bold">
              {aiState}
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
              aiState={aiState} 
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
                activePersonality === "zora"
                  ? "bg-purple-500/10 border-purple-400/20 text-purple-300 shadow-[0_0_15px_rgba(192,132,252,0.15)]"
                  : "bg-emerald-500/10 border-emerald-400/20 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.15)]"
              }`}
            >
              {activePersonality === "zora" ? "Zora Online" : "Ultron Online"}
            </button>

            {/* Mic icon */}
            <button className="text-white/20 hover:text-white/50 transition-colors px-2">
              🎙️
            </button>
          </div>

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
              <config.Component />
            </React.Suspense>
          </WidgetContainer>
        );
      })}

    </div>
  );
}
