import React, { useState, useEffect } from 'react';

/**
 * FileExplorerWidget — real project browser (Set B: no fake D:\ drives).
 * Lists the actual project directory via the backend list_contents tool.
 */
export default function FileExplorerWidget() {
  const [path, setPath] = useState(".");
  const [entries, setEntries] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = async (folder) => {
    setLoading(true); setError("");
    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${apiUrl}/api/tools/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tool_id: "list_contents", arguments: { folderpath: folder }, has_confirmed: true })
      });
      const data = await res.json();
      if (data.success && data.data?.contents) {
        setEntries(data.data.contents);
        setPath(folder);
      } else {
        setError(data.error || "cannot list folder");
      }
    } catch (err) { setError("offline"); } finally { setLoading(false); }
  };

  useEffect(() => { load("."); }, []);

  return (
    <div className="space-y-2 font-mono text-[9px]">
      <div className="flex items-center gap-2 text-[8px] text-white/40 truncate">
        <button onClick={() => load(".")} className="text-[#7DD3FC] hover:underline">root</button>
        <span>/</span>
        <span className="truncate text-white/60">{path}</span>
      </div>
      {error && <p className="text-rose-400">{error}</p>}
      {loading ? <p className="text-white/25">Loading…</p> : (
        <div className="space-y-1 max-h-40 overflow-y-auto">
          {entries.length === 0 && <p className="text-white/25">(empty)</p>}
          {entries.map((e, i) => (
            <button key={i} onClick={() => e.type === "folder" && load(`${path === "." ? "" : path}/${e.name}`)}
              className="flex w-full items-center justify-between text-left text-[#F5F5F7] hover:bg-white/5 rounded-sm px-1">
              <span className={e.type === "folder" ? "text-[#7DD3FC]" : ""}>
                {e.type === "folder" ? "📁 " : "📄 "}{e.name}
              </span>
              <span className="text-white/30 text-[8px]">{e.type === "file" && e.size ? e.size : ""}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
