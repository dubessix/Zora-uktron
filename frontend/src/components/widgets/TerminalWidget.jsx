import React from 'react';

/**
 * TerminalWidget Content Component
 * Demonstrates local subprocess command runners, running logs, and compiler statuses.
 */
export default function TerminalWidget() {
  const terminal_logs = [
    { line: "$ npm run build", type: "cmd" },
    { line: "vite v5.3.1 building for production...", type: "info" },
    { line: "✓ 142 modules transformed.", type: "success" },
    { line: "dist/index.html                  0.42 kB │ gzip: 0.12 kB", type: "log" },
    { line: "dist/assets/index-B_024f2b.js   145.42 kB │ gzip: 42.12 kB", type: "log" },
    { line: "✓ built in 3.42s", type: "success" }
  ];

  return (
    <div className="space-y-3 font-mono text-[9px]">
      
      {/* Console log outputs */}
      <div className="bg-[#0A0A0F] border border-white/5 p-3 rounded-sm space-y-1.5 h-44 overflow-y-auto font-mono text-[#7DD3FC]">
        {terminal_logs.map((log, idx) => (
          <div key={idx} className="leading-relaxed whitespace-pre-wrap select-text">
            <span className={
              log.type === "cmd" ? "text-emerald-400 font-bold" :
              log.type === "success" ? "text-emerald-400" :
              log.type === "info" ? "text-[#8B8B96]" : "text-sky-200"
            }>
              {log.line}
            </span>
          </div>
        ))}
      </div>

    </div>
  );
}
