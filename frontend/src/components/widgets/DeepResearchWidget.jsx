import React from 'react';

/**
 * DeepResearchWidget Content Component
 * Powered theoretically by Tavily API, demonstrating AI multi-source search summaries.
 */
export default function DeepResearchWidget() {
  const findings = {
    topic: "AI Agents Architecture",
    summary: "AI Agents are progressing towards autonomous, multi-step execution flows using tools, vector stores, and cognitive planning routers. Current industry patterns are shifting from static RAG to dynamic, event-driven, multi-agent frameworks.",
    sources: [
      { name: "Tavily AI Index", url: "https://tavily.com" },
      { name: "LangChain Research", url: "https://langchain.com" }
    ]
  };

  return (
    <div className="space-y-4 font-mono text-[10px]">
      {/* Topic Title */}
      <div className="bg-[#7DD3FC]/5 border border-[#7DD3FC]/10 p-2.5 rounded-sm">
        <span className="block text-[7px] text-[#7DD3FC] uppercase tracking-widest font-bold">Research Topic</span>
        <p className="text-xs font-bold text-[#F5F5F7] mt-1">{findings.topic}</p>
      </div>

      {/* Summary Content */}
      <div className="space-y-2">
        <span className="text-[7px] text-[#8B8B96] uppercase tracking-widest font-bold">AI Summary</span>
        <p className="text-[9px] text-[#F5F5F7] leading-relaxed bg-white/[0.01] border border-white/5 p-3 rounded-sm">
          {findings.summary}
        </p>
      </div>

      {/* Source Links */}
      <div className="space-y-1.5">
        <span className="text-[7px] text-[#8B8B96] uppercase tracking-widest font-bold">Sources Identified</span>
        <div className="flex gap-2 flex-wrap">
          {findings.sources.map((source, idx) => (
            <a 
              key={idx}
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[8px] bg-white/5 hover:bg-white/10 px-2 py-1 rounded-sm border border-white/5 text-[#7DD3FC] underline"
            >
              {source.name}
            </a>
          ))}
        </div>
      </div>

      {/* Save findings hook */}
      <button 
        onClick={() => print("Findings committed to Long-Term Memory.")}
        className="w-full py-1.5 border border-white/10 bg-white/5 text-[9px] uppercase tracking-widest font-bold hover:bg-white/10"
      >
        Commit to Memory
      </button>

    </div>
  );
}

function print(msg) {
  console.log(msg);
}
