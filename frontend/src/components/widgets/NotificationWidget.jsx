import React from 'react';

/**
 * NotificationWidget Content Component
 * Displays system alerts, background task finishes, and calendar clocks.
 */
export default function NotificationWidget() {
  const alerts = [
    { title: "Task Completed", message: "SQLite vector deduplication script run finished. (Pruned 42 rows)", priority: "medium", time: "12m ago" },
    { title: "Calendar Reminder", message: "Verifying server Stripe webhooks starts in 1 hour.", priority: "high", time: "45m ago" }
  ];

  return (
    <div className="space-y-3 font-mono text-[10px]">
      
      {/* Dynamic Alerts stack */}
      <div className="space-y-2 max-h-48 overflow-y-auto">
        {alerts.map((alert, idx) => (
          <div 
            key={idx}
            className="p-2 border border-white/5 bg-white/[0.01] rounded-sm flex flex-col gap-1"
          >
            <div className="flex justify-between items-center">
              <span className="font-bold text-[#F5F5F7] text-[9px] uppercase tracking-wider truncate max-w-[70%]">{alert.title}</span>
              <span className="text-[6px] text-white/30 uppercase font-mono">{alert.time}</span>
            </div>
            <p className="text-[9px] text-[#8B8B96] leading-relaxed mt-0.5">{alert.message}</p>
            <span className={`text-[6px] uppercase tracking-widest font-bold mt-1.5 inline-block px-1 rounded-sm w-fit ${
              alert.priority === "high" ? "bg-rose-500/10 text-rose-400" : "bg-emerald-500/10 text-emerald-400"
            }`}>
              {alert.priority} priority
            </span>
          </div>
        ))}
      </div>

    </div>
  );
}
