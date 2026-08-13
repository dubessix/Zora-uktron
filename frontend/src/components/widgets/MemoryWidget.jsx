import React, { useState, useEffect } from 'react';

/**
 * MemoryWidget — real memory viewer (Set B: no fake counts).
 * Fetches real vector_memories from the backend.
 */
export default function MemoryWidget() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
        const res = await fetch(`${apiUrl}/api/memory/recent?limit=5`);
        if (res.ok) setData(await res.json());
      } catch (err) { /* offline */ } finally { setLoading(false); }
    };
    load();
  }, []);

  const memories = data?.memories || [];
  const total = data?.total ?? 0;

  return (
    <div className="space-y-3 font-mono text-[10px]">
      <div className="flex justify-between items-center bg-white/5 p-2 rounded-sm text-[8px] text-[#8B8B96] uppercase tracking-wider font-bold">
        <span>Recent Memories Indexed</span>
        <span>Total: {loading ? "…" : total}</span>
      </div>

      <div className="space-y-2 max-h-48 overflow-y-auto">
        {loading ? (
          <p className="text-[9px] text-white/30">Loading memories…</p>
        ) : memories.length === 0 ? (
          <p className="text-[9px] text-white/30">No memories stored yet.</p>
        ) : memories.map((mem, idx) => (
          <div key={idx} className="p-2 border border-white/5 bg-white/[0.01] rounded-sm flex flex-col gap-1.5">
            <p className="text-[9px] text-[#F5F5F7] leading-relaxed select-text font-mono">"{mem.content}"</p>
            <div className="flex justify-between items-center text-[7px] uppercase tracking-widest font-bold mt-1 text-white/40">
              <span className="text-[#7DD3FC]">{mem.type}</span>
              <span>{mem.created_at || ""}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
