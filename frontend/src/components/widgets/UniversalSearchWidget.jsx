import React, { useState } from 'react';

/**
 * UniversalSearchWidget Content Component
 * Single unified search interface for files, apps, memories, and projects.
 */
export default function UniversalSearchWidget() {
  const [query, setQuery] = useState("");
  const allRecords = [
    { name: "package.json", category: "File", detail: "D:\\SaaS-Builds\\package.json" },
    { name: "Webpack Loader mismatch fix", category: "Memory", detail: "Phase 3 persistent store" },
    { name: "Vite dev compiler", category: "Application", detail: "Ready on Port 5173" },
    { name: "Git active branch: main", category: "Project", detail: "3 modified changes staged" },
    { name: "Deploy payment webhook", category: "Todo", detail: "High priority task" }
  ];

  const filtered = query.trim() 
    ? allRecords.filter(item => item.name.toLowerCase().includes(query.toLowerCase()) || item.category.toLowerCase().includes(query.toLowerCase()))
    : allRecords;

  return (
    <div className="space-y-3 font-mono text-[10px]">
      {/* Search Input Box */}
      <input 
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search files, apps, projects, memories..."
        className="w-full bg-white/[0.02] border border-white/5 rounded-sm px-3 py-2 text-[10px] text-[#F5F5F7] placeholder-white/20 focus:outline-none focus:border-[#7DD3FC]/30"
      />

      {/* Query Matches List */}
      <div className="space-y-2 max-h-48 overflow-y-auto">
        {filtered.map((item, idx) => (
          <div 
            key={idx}
            className="p-2 border border-white/5 bg-white/[0.01] rounded-sm flex flex-col gap-1"
          >
            <div className="flex justify-between items-center">
              <span className="font-bold text-[#F5F5F7]">{item.name}</span>
              <span className="text-[7px] bg-[#7DD3FC]/10 text-[#7DD3FC] px-1.5 py-0.5 rounded-sm font-bold uppercase tracking-wider">{item.category}</span>
            </div>
            <span className="text-[8px] text-white/30 truncate">{item.detail}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
