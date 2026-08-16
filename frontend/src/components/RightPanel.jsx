import React, { useState, useRef, useEffect } from 'react';
import { ChevronRight, CircleCheck, Send } from 'lucide-react';
import { getPersonalityTheme } from '../theme/personalityTheme';

/**
 * RightPanel — Chat + Log tabs.
 * Chat = conversation (as before). Log = Ultron's real-time operational
 * activity (tool calls, results, errors) streamed from the backend.
 */
export default function RightPanel({ 
  messages, 
  inputValue, 
  setInputValue, 
  handleSendMessage, 
  isProcessing, 
  activePersonality,
  backendStatus,
  logs = []
}) {
  const [tab, setTab] = useState("chat");
  const scrollRef = useRef(null);
  const logScrollRef = useRef(null);
  const activeTheme = getPersonalityTheme(activePersonality);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    logScrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <aside className="col-span-12 lg:col-span-3 h-full flex flex-col gap-4 bg-[#0B1112]/72 border border-white/[0.07] p-4 rounded-xl backdrop-blur-xl">
      
      {/* Header + Chat/Log tabs */}
      <div className="flex items-center justify-between border-b border-white/5 pb-3">
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setTab("chat")}
            className={`text-[9px] uppercase font-bold tracking-widest px-3 py-1 rounded-full border transition-colors ${
              tab === "chat" ? "" : "border-transparent text-white/40 hover:text-white/70"
            }`}
            style={tab === "chat" ? {
              color: activeTheme.primary,
              backgroundColor: activeTheme.surface,
              borderColor: activeTheme.border,
            } : undefined}
          >
            Chat
          </button>
          <button
            onClick={() => setTab("log")}
            className={`text-[9px] uppercase font-bold tracking-widest px-3 py-1 rounded-full transition-colors ${
              tab === "log" ? "bg-[#7DD3FC]/10 text-[#7DD3FC] border border-[#7DD3FC]/20" : "text-white/40 hover:text-white/70"
            }`}
          >
            Log
          </button>
        </div>
        <span className={`text-[8px] border px-2 py-0.5 rounded-full font-mono tracking-wider ${backendStatus === 'CONNECTED' ? 'border-emerald-500/20 bg-emerald-500/5 text-emerald-400' : 'border-amber-500/20 bg-amber-500/5 text-amber-300'}`}>
          {backendStatus || 'UNKNOWN'}
        </span>
      </div>

      {/* CHAT TAB */}
      {tab === "chat" && (
        <div className="flex-1 overflow-y-auto space-y-4 pr-1 scrollbar-thin">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center p-4 gap-4">
              <div className="w-8 h-8 rounded-full border border-[#7DD3FC]/10 bg-[#7DD3FC]/5 flex items-center justify-center text-[#7DD3FC] animate-pulse">
                <CircleCheck size={16} strokeWidth={1.8} aria-hidden="true" />
              </div>
              <p className="text-[10px] text-[#8B8B96] leading-relaxed uppercase tracking-wider font-mono">
                {backendStatus === 'CONNECTED'
                  ? 'Backend connected. Tap the mic or type below to begin.'
                  : 'Backend is not connected. Start the local service before sending a message.'}
              </p>
            </div>
          ) : (
            messages.map((msg) => {
              const isUser = msg.sender === "user";
              const messageTheme = getPersonalityTheme(msg.personality);
              return (
                <div key={msg.id} className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}>
                  <div
                    className={`max-w-[90%] p-3.5 rounded-2xl border backdrop-blur-md transition-all ${
                      isUser
                        ? "bg-[#10B981]/5 border-emerald-500/10 text-[#F5F5F7] rounded-tr-none"
                        : "rounded-tl-none"
                    }`}
                    style={isUser ? undefined : {
                      backgroundColor: messageTheme.surface,
                      borderColor: messageTheme.border,
                      color: messageTheme.text,
                    }}
                  >
                    <span className="block text-[7px] opacity-40 uppercase tracking-widest mb-1.5 font-bold">
                      {isUser ? "Debjeet" : msg.personality ? msg.personality : "System"}
                    </span>
                    <p className="text-[10px] leading-relaxed font-mono select-text whitespace-pre-wrap">{msg.text}</p>
                    {msg.sender === "ai" && msg.response_ms !== undefined && (
                      <span className="block text-[6px] text-right opacity-30 mt-1.5 tracking-wider uppercase font-mono">
                        {msg.response_ms}ms
                      </span>
                    )}
                  </div>
                </div>
              );
            })
          )}
          <div ref={scrollRef} />
        </div>
      )}

      {/* LOG TAB — real-time operational activity */}
      {tab === "log" && (
        <div className="flex-1 overflow-y-auto pr-1 scrollbar-thin bg-black/30 border border-white/5 rounded-sm p-2 space-y-1 font-mono text-[9px]">
          {logs.length === 0 ? (
            <p className="text-white/30">No activity yet. Ask Ultron to run a tool — you'll see real-time logs here.</p>
          ) : (
            logs.map((l, i) => (
              <div key={i} className="flex items-start gap-2">
                <span className={l.level === "error" ? "text-rose-400" : l.level === "success" ? "text-emerald-400" : "text-[#7DD3FC]"}>
                  <ChevronRight size={12} strokeWidth={1.8} aria-hidden="true" />
                </span>
                <span className={l.level === "error" ? "text-rose-300" : l.level === "success" ? "text-emerald-300" : "text-white/70"}>
                  {l.message}
                </span>
              </div>
            ))
          )}
          <div ref={logScrollRef} />
        </div>
      )}

      {/* Rounded text query input box (shared) */}
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
            className="text-xs ml-2 transition-all disabled:opacity-20"
            style={{ color: activeTheme.primary }}
            aria-label="Send message"
            title="Send message"
          >
            <Send size={14} strokeWidth={1.8} aria-hidden="true" />
          </button>
        </div>
      </form>
    </aside>
  );
}
