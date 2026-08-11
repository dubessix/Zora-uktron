import React from 'react';

/**
 * LeftPanel Component
 * Renders the System Overview sparklines card, Network Telemetry card,
 * and individual resource performance meters (CPU, RAM, Temp, OS).
 * Designed strictly matching the reference image layout.
 */
export default function LeftPanel({ systemMetrics }) {
  // Extract real-time metrics or fallback to standard target parameters
  const ramUsagePercent = systemMetrics ? systemMetrics.total_system_ram_usage_percent : 82.2;
  const cpuPercent = systemMetrics ? systemMetrics.cpu_percent : 37.2;

  return (
    <aside className="col-span-12 lg:col-span-3 h-full flex flex-col gap-4 overflow-y-auto pr-1">
      
      {/* ==============================================================================
          1. SYSTEM OVERVIEW SPARKLINE CARD (Widescreen Mockup Top Left)
         ============================================================================== */}
      <div className="bg-[#14141E]/80 border border-white/5 p-4 rounded-sm backdrop-blur-2xl">
        <div className="flex justify-between items-center mb-3">
          <span className="text-[9px] uppercase font-bold tracking-widest text-[#F5F5F7]">
            ✦ System Overview
          </span>
          <span className="text-[7px] text-emerald-400 tracking-widest font-mono uppercase">
            ✦ LIVE
          </span>
        </div>

        {/* 4-Meters Grid with Inline Sparkline SVGs */}
        <div className="grid grid-cols-2 gap-3 font-mono text-[10px]">
          {/* CPU Sparkline */}
          <div className="bg-white/[0.01] border border-white/5 p-2 rounded-sm flex items-center justify-between">
            <div>
              <span className="text-[7px] text-[#8B8B96] uppercase tracking-wider block">CPU</span>
              <span className="text-sm font-bold text-emerald-400 mt-1 block">{cpuPercent.toFixed(0)}%</span>
            </div>
            {/* Emerald Glowing Sparkline */}
            <svg className="w-16 h-8 drop-shadow-[0_0_4px_rgba(52,211,153,0.3)]" viewBox="0 0 100 30">
              <path d="M 0,25 Q 20,5 40,20 T 80,10 T 100,15" fill="none" stroke="#34D399" strokeWidth="1.5" />
            </svg>
          </div>

          {/* RAM Sparkline */}
          <div className="bg-white/[0.01] border border-white/5 p-2 rounded-sm flex items-center justify-between">
            <div>
              <span className="text-[7px] text-[#8B8B96] uppercase tracking-wider block">RAM</span>
              <span className="text-sm font-bold text-amber-400 mt-1 block">{ramUsagePercent.toFixed(0)}%</span>
            </div>
            {/* Amber Glowing Sparkline */}
            <svg className="w-16 h-8 drop-shadow-[0_0_4px_rgba(251,191,36,0.3)]" viewBox="0 0 100 30">
              <path d="M 0,20 Q 20,25 40,10 T 80,18 T 100,5" fill="none" stroke="#FBBF24" strokeWidth="1.5" />
            </svg>
          </div>

          {/* Temperature Sparkline */}
          <div className="bg-white/[0.01] border border-white/5 p-2 rounded-sm flex items-center justify-between">
            <div>
              <span className="text-[7px] text-[#8B8B96] uppercase tracking-wider block">Temp</span>
              <span className="text-sm font-bold text-rose-400 mt-1 block">55°C</span>
            </div>
            {/* Rose Glowing Sparkline */}
            <svg className="w-16 h-8 drop-shadow-[0_0_4px_rgba(251,113,133,0.3)]" viewBox="0 0 100 30">
              <path d="M 0,15 Q 20,10 40,22 T 80,5 T 100,12" fill="none" stroke="#FB7185" strokeWidth="1.5" />
            </svg>
          </div>

          {/* Disk Space Sparkline */}
          <div className="bg-white/[0.01] border border-white/5 p-2 rounded-sm flex items-center justify-between">
            <div>
              <span className="text-[7px] text-[#8B8B96] uppercase tracking-wider block">Disk</span>
              <span className="text-sm font-bold text-purple-400 mt-1 block">62%</span>
            </div>
            {/* Purple Glowing Sparkline */}
            <svg className="w-16 h-8 drop-shadow-[0_0_4px_rgba(192,132,252,0.3)]" viewBox="0 0 100 30">
              <path d="M 0,22 Q 20,18 40,5 T 80,25 T 100,10" fill="none" stroke="#C084FC" strokeWidth="1.5" />
            </svg>
          </div>
        </div>
      </div>

      {/* ==============================================================================
          2. NETWORK TELEMETRY LINK CARD
         ============================================================================== */}
      <div className="bg-[#14141E]/80 border border-white/5 p-4 rounded-sm backdrop-blur-2xl">
        <div className="flex justify-between items-center mb-3">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#7DD3FC] animate-pulse" />
            <h2 className="text-[10px] uppercase font-bold tracking-widest text-[#F5F5F7]">
              Network Telemetry Link
            </h2>
          </div>
          <span className="text-[8px] border border-emerald-500/20 bg-emerald-500/5 px-2 py-0.5 rounded-full text-emerald-400 font-mono tracking-wider">
            CONNECTED
          </span>
        </div>

        {/* Latency and Uptime Grid */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-white/[0.01] border border-white/5 p-2.5 rounded-sm">
            <span className="block text-[7px] text-[#8B8B96] uppercase tracking-widest">Latency</span>
            <span className="text-sm font-bold text-[#7DD3FC] mt-1 block">31 <span className="text-[9px]">ms</span></span>
          </div>
          <div className="bg-white/[0.01] border border-white/5 p-2.5 rounded-sm">
            <span className="block text-[7px] text-[#8B8B96] uppercase tracking-widest">Uptime</span>
            <span className="text-sm font-bold text-emerald-400 mt-1 block">3.0 <span className="text-[9px]">h</span></span>
          </div>
        </div>

        {/* TX/RX Signal Lines */}
        <div className="space-y-3 font-mono">
          <div>
            <div className="flex justify-between text-[7px] text-[#8B8B96] uppercase mb-1 tracking-wider">
              <span>TX Signal load</span>
              <span>43%</span>
            </div>
            <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
              <div className="h-full bg-pink-500 rounded-full" style={{ width: "43%" }} />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-[7px] text-[#8B8B96] uppercase mb-1 tracking-wider">
              <span>RX Signal load</span>
              <span>62%</span>
            </div>
            <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
              <div className="h-full bg-[#7DD3FC] rounded-full" style={{ width: "62%" }} />
            </div>
          </div>
        </div>
      </div>

      {/* ==============================================================================
          3. CPU, RAM, TEMP & OS METERS (Mockup Bottom Left Panel Column)
         ============================================================================== */}
      <div className="grid grid-cols-2 gap-3">
        {/* CPU Panel */}
        <div className="bg-[#14141E]/80 border border-white/5 p-3 rounded-sm backdrop-blur-2xl">
          <span className="text-[8px] uppercase tracking-widest text-[#8B8B96] block">CPU Load</span>
          <span className="text-sm font-bold text-emerald-400 mt-1.5 block font-mono">
            {cpuPercent.toFixed(1)}%
          </span>
          <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden mt-2.5">
            <div className="h-full bg-emerald-400 rounded-full" style={{ width: `${cpuPercent}%` }} />
          </div>
        </div>

        {/* RAM Panel */}
        <div className="bg-[#14141E]/80 border border-white/5 p-3 rounded-sm backdrop-blur-2xl">
          <span className="text-[8px] uppercase tracking-widest text-[#8B8B96] block">RAM Usage</span>
          <span className="text-sm font-bold text-[#FB7185] mt-1.5 block font-mono">
            {ramUsagePercent.toFixed(1)}%
          </span>
          <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden mt-2.5">
            <div className="h-full bg-[#FB7185] rounded-full" style={{ width: `${ramUsagePercent}%` }} />
          </div>
        </div>

        {/* Temperature Panel */}
        <div className="bg-[#14141E]/80 border border-white/5 p-3 rounded-sm backdrop-blur-2xl">
          <span className="text-[8px] uppercase tracking-widest text-[#8B8B96] block">Temperature</span>
          <span className="text-sm font-bold text-sky-400 mt-1.5 block font-mono">
            55.0°C
          </span>
          <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden mt-2.5">
            <div className="h-full bg-sky-400 rounded-full" style={{ width: "55%" }} />
          </div>
        </div>

        {/* OS Panel */}
        <div className="bg-[#14141E]/80 border border-white/5 p-3 rounded-sm backdrop-blur-2xl flex flex-col justify-between">
          <div>
            <span className="text-[8px] uppercase tracking-widest text-[#8B8B96] block">System Status</span>
            <span className="text-[10px] font-bold text-[#F5F5F7] mt-1 block font-mono truncate">
              {navigator.userAgent.includes("Windows") ? "WIN 11" : "UBUNTU 24.04"}
            </span>
          </div>
          <span className="text-[7px] bg-purple-500/10 text-purple-300 border border-purple-500/20 px-1.5 py-0.5 rounded-sm uppercase tracking-wider font-mono w-fit mt-1">
            ACTIVE
          </span>
        </div>
      </div>

    </aside>
  );
}
