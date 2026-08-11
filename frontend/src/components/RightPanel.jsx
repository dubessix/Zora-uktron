import React, { useRef, useEffect } from 'react';

/**
 * RightPanel Component
 * Renders the clean, monospace conversation dialogue log and circular text query input bar.
 */
export default function RightPanel({ 
  messages, 
  inputValue, 
  setInputValue, 
  handleSendMessage, 
  isProcessing, 
  activePersonality 
}) {
  const scrollRef = useRef(null);

  // Auto-scroll on new message append
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <aside className="col-span-12 lg:col-span-3 h-full flex flex-col gap-4 bg-white/[0.01] border border-white/5 p-4 rounded-sm backdrop-blur-xl">
      
      {/* Dialogue Header */}
      <div className="flex justify-between items-center border-b border-white/5 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <h2 className="text-[10px] uppercase font-bold tracking-widest text-[#F5F5F7]">
            Conversation
          </h2>
        </div>
        <span className="text-[8px] border border-emerald-500/20 bg-emerald-500/5 px-2 py-0.5 rounded-full text-emerald-400 font-mono tracking-wider">
          LIVE
        </span>
      </div>

      {/* Chat Messages Log view */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-4 gap-4">
            <div className="w-8 h-8 rounded-full border border-[#7DD3FC]/10 bg-[#7DD3FC]/5 flex items-center justify-center text-[#7DD3FC] animate-pulse">
              ✓
            </div>
            <p className="text-[10px] text-[#8B8B96] leading-relaxed uppercase tracking-wider font-mono">
              System online. Speak "Hey Ultron" or type below to begin.
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <div 
              key={msg.id} 
              className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"}`}
            >
              <div 
                className={`max-w-[90%] p-3.5 rounded-2xl border backdrop-blur-md transition-all ${
                  msg.sender === "user"
                    ? "bg-[#10B981]/5 border-emerald-500/10 text-[#F5F5F7] rounded-tr-none"
                    : msg.personality === "zora"
                    ? "bg-purple-500/5 border-purple-400/10 text-purple-200 rounded-tl-none"
                    : "bg-[#7DD3FC]/5 border-sky-500/10 text-sky-200 rounded-tl-none"
                }`}
              >
                <span className="block text-[7px] opacity-35 uppercase tracking-widest mb-1.5 font-bold">
                  {msg.sender === "user" ? "Debjeet" : msg.personality ? msg.personality : "System"}
                </span>
                <p className="text-[10px] leading-relaxed font-mono select-text whitespace-pre-wrap">
                  {msg.text}
                </p>
                {msg.sender === "ai" && msg.response_ms !== undefined && (
                  <span className="block text-[6px] text-right opacity-30 mt-1.5 tracking-wider uppercase font-mono">
                    {msg.response_ms}ms // fast
                  </span>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={scrollRef} />
      </div>

      {/* Rounded text query input box from reference image */}
      <form onSubmit={handleSendMessage} className="flex gap-2 border-t border-white/5 pt-3">
        <div className="flex-1 flex items-center bg-white/[0.02] border border-white/5 rounded-full px-4 py-2 focus-within:border-[#7DD3FC]/30 transition-colors">
          <input 
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isProcessing}
            placeholder={isProcessing ? "Processing..." : "Ask anything, Ultron is listening..."}
            className="flex-1 bg-transparent text-[10px] text-[#F5F5F7] placeholder-white/20 focus:outline-none font-mono"
          />
          <button
            type="submit"
            disabled={isProcessing || !inputValue.trim()}
            className={`text-xs ml-2 transition-all disabled:opacity-20 ${
              activePersonality === "zora" ? "text-purple-300" : "text-emerald-400"
            }`}
          >
            ➤
          </button>
        </div>
      </form>
    </aside>
  );
}
