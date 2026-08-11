import React from 'react';

/**
 * MemoryWidget Content Component
 * Displays recent database indices, long-term context triggers, and user profile values.
 */
export default function MemoryWidget() {
  const memories = [
    { text: "User prefers React 19 over Angular", category: "persistent", confidence: "1.00" },
    { text: "Learned: JWT is used for stateless authentication tokens", category: "semantic", confidence: "0.98" },
    { text: "Struggled with CORS policy error last night", category: "episodic", confidence: "0.91" }
  ];

  return (
    <div className="space-y-3 font-mono text-[10px]">
      
      {/* Database status counts */}
      <div className="flex justify-between items-center bg-white/5 p-2 rounded-sm text-[8px] text-[#8B8B96] uppercase tracking-wider font-bold">
        <span>Recent Memories Indexed</span>
        <span>Total Count: 1,402</span>
      </div>

      {/* Memories loop */}
      <div className="space-y-2 max-h-48 overflow-y-auto">
        {memories.map((mem, idx) => (
          <div 
            key={idx}
            className="p-2 border border-white/5 bg-white/[0.01] rounded-sm flex flex-col gap-1.5"
          >
            <p className="text-[9px] text-[#F5F5F7] leading-relaxed select-text font-mono">
              "{mem.text}"
            </p>
            <div className="flex justify-between items-center text-[7px] uppercase tracking-widest font-bold mt-1 text-white/40">
              <span className="text-[#7DD3FC]">{mem.category}</span>
              <span>Confidence: {mem.confidence}</span>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}
