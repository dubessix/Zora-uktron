import React, { useState, useEffect } from 'react';

/**
 * DailyBriefingWidget Component
 * Compiles today's schedules, weather, high priority backlog lists,
 * and AI News monitor results natively (Jarvis-style Protocol).
 */
export default function DailyBriefingWidget() {
  const [loading, setLoading] = useState(false);
  const [briefing, setBriefing] = useState(null);

  const fetchBriefing = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/tools/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool_id: 'daily_briefing',
          arguments: {
            include_weather: true,
            include_tasks: true,
            include_schedule: true
          }
        })
      });
      const data = await response.json();
      if (data.success) {
        setBriefing(data.data);
      }
    } catch (e) {
      console.error('Failed to build briefing:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBriefing();
  }, []);

  return (
    <div className="flex flex-col h-full w-full font-mono text-[10px] text-white/90 p-4 space-y-4 overflow-y-auto custom-scrollbar">
      
      {/* Header */}
      <div className="flex justify-between items-center border-b border-white/5 pb-2">
        <span className="text-[11px] font-bold tracking-widest text-[#7DD3FC] uppercase">
          🌅 Morning Briefing
        </span>
        <button
          onClick={fetchBriefing}
          disabled={loading}
          className="bg-[#7DD3FC]/10 hover:bg-[#7DD3FC]/20 border border-[#7DD3FC]/30 text-[#7DD3FC] text-[8px] px-2 py-0.5 rounded-sm uppercase tracking-wider"
        >
          {loading ? 'Compiling...' : 'Refresh'}
        </button>
      </div>

      {/* Main Contents */}
      {!briefing ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center text-white/30 uppercase py-6">
          <span>Compiling today's dashboard report, Sir...</span>
        </div>
      ) : (
        <div className="space-y-3 flex-1 overflow-y-auto max-h-[220px] custom-scrollbar text-[9px] uppercase">
          
          {/* Quick weather badge from API */}
          <div className="bg-white/5 p-2 rounded-sm flex justify-between items-center border border-white/5">
            <div>
              <span className="text-white/40 block text-[7px]">DATE</span>
              <span className="font-bold text-[#7DD3FC]">{briefing.date}</span>
            </div>
            <div className="text-right">
              <span className="text-white/40 block text-[7px]">WEATHER</span>
              <span className="font-bold text-[#7DD3FC]">
                {briefing.weather.temperature} ({briefing.weather.windspeed})
              </span>
            </div>
          </div>

          {/* Formatted Text Box */}
          <div className="bg-white/[0.01] border border-white/5 p-3 rounded-sm leading-relaxed whitespace-pre-wrap text-white/80 lowercase first-letter:uppercase">
            {briefing.briefing_text}
          </div>

        </div>
      )}

    </div>
  );
}
