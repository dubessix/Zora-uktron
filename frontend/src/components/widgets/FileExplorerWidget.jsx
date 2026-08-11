import React, { useState } from 'react';

/**
 * FileExplorerWidget Content Component
 * Renders local directories, disk drives (D:), downloads, and file structures.
 */
export default function FileExplorerWidget() {
  const [currentPath, setCurrentPath] = useState("D:\\SaaS-Builds\\");
  const [files, setFiles] = useState([
    { name: "src", type: "folder" },
    { name: "public", type: "folder" },
    { name: "package.json", type: "file", size: "1.2 KB" },
    { name: "vite.config.js", type: "file", size: "640 B" },
    { name: "README.md", type: "file", size: "4.2 KB" }
  ]);

  const handleNavigate = (dir) => {
    if (dir === "D:\\") {
      setCurrentPath("D:\\");
      setFiles([
        { name: "SaaS-Builds", type: "folder" },
        { name: "Documents", type: "folder" },
        { name: "Downloads", type: "folder" },
        { name: "backups", type: "folder" }
      ]);
    } else if (dir === "Downloads") {
      setCurrentPath("D:\\Downloads\\");
      setFiles([
        { name: "node-v20-linux.tar.gz", type: "file", size: "42 MB" },
        { name: "stripe-webhook-test.sh", type: "file", size: "1.5 KB" }
      ]);
    } else {
      setCurrentPath(`D:\\SaaS-Builds\\${dir}\\`);
      setFiles([
        { name: "App.jsx", type: "file", size: "12 KB" },
        { name: "main.jsx", type: "file", size: "1.1 KB" }
      ]);
    }
  };

  return (
    <div className="space-y-3 font-mono text-[10px]">
      {/* Path bar and quick shortcuts */}
      <div className="flex justify-between items-center bg-white/5 p-2 rounded-sm text-[#8B8B96]">
        <span className="truncate max-w-[70%] font-bold text-[#F5F5F7]">{currentPath}</span>
        <div className="flex gap-2">
          <button onClick={() => handleNavigate("D:\\")} className="hover:text-white uppercase tracking-wider text-[8px] font-bold">D: Drive</button>
          <button onClick={() => handleNavigate("Downloads")} className="hover:text-white uppercase tracking-wider text-[8px] font-bold">Downloads</button>
        </div>
      </div>

      {/* Files List */}
      <div className="space-y-1.5 max-h-48 overflow-y-auto">
        {files.map((file, idx) => (
          <div 
            key={idx}
            onClick={() => file.type === "folder" && handleNavigate(file.name)}
            className={`flex justify-between items-center p-1.5 rounded-sm hover:bg-white/5 ${file.type === "folder" ? "cursor-pointer" : "cursor-default"}`}
          >
            <span className="flex items-center gap-2">
              <span className={file.type === "folder" ? "text-[#7DD3FC]" : "text-white/40"}>
                {file.type === "folder" ? "📁" : "📄"}
              </span>
              <span className={file.type === "folder" ? "text-[#7DD3FC] font-bold" : "text-[#F5F5F7]"}>
                {file.name}
              </span>
            </span>
            {file.size && <span className="text-[8px] text-white/30">{file.size}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
