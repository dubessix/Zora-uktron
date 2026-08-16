import React, { useState } from 'react';
import { Plus, Settings, X } from 'lucide-react';
import { WIDGET_REGISTRY } from './widgets/WidgetManager';

/**
 * Far-left launcher rail. It only opens/closes existing centre overlays; widget
 * rendering, dragging, sizing, and backend contracts remain owned elsewhere.
 */
export default function WidgetRail({ widgetState, toggleWidget, activePersonality }) {
  const [expanded, setExpanded] = useState(false);
  const isZora = activePersonality === "zora";
  const activeText = isZora ? "text-pink-400" : "text-emerald-400";
  const activeBorder = isZora ? "border-pink-400/35" : "border-emerald-400/35";
  const activeBackground = isZora ? "bg-pink-500/10" : "bg-emerald-500/10";
  const activeIndicator = isZora ? "bg-pink-400" : "bg-emerald-400";

  return (
    <aside
      className="relative z-[1200] h-screen w-14 shrink-0 border-r border-white/[0.06]"
      aria-label="Widget launcher"
    >
      <div className={`absolute inset-y-0 left-0 flex h-full flex-col bg-[#080B0F]/95 px-1.5 py-3 font-mono backdrop-blur-xl transition-[width] duration-200 ${
        expanded ? "w-52" : "w-14"
      } ${expanded ? "shadow-[12px_0_30px_rgba(0,0,0,0.45)]" : ""}`}>
        <div className="flex-1 space-y-1 overflow-y-auto overflow-x-hidden pr-0.5 scrollbar-thin">
          {Object.entries(WIDGET_REGISTRY).map(([widgetId, config]) => {
            const Icon = config.icon;
            const isVisible = Boolean(widgetState[widgetId]?.visible);
            return (
              <button
                key={widgetId}
                type="button"
                onClick={() => toggleWidget(widgetId)}
                aria-label={`Open ${config.title}`}
                aria-pressed={isVisible}
                title={config.title}
                className={`group relative flex h-10 w-full items-center rounded-lg border transition-colors duration-150 ${
                  expanded ? "justify-start gap-3 px-2.5" : "justify-center px-0"
                } ${
                  isVisible
                    ? `${activeBorder} ${activeBackground} ${activeText}`
                    : "border-transparent text-white/38 hover:border-white/10 hover:bg-white/[0.04] hover:text-white/75"
                }`}
              >
                {isVisible && (
                  <span
                    className={`absolute -left-1.5 h-5 w-0.5 rounded-r-full ${activeIndicator}`}
                    aria-hidden="true"
                  />
                )}
                <Icon size={18} strokeWidth={1.7} aria-hidden="true" className="shrink-0" />
                {expanded && (
                  <span className="truncate text-left text-[10px] font-semibold tracking-wide">
                    {config.title}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        <div className="mt-2 space-y-1 border-t border-white/[0.07] pt-2">
          <button
            type="button"
            onClick={() => setExpanded((current) => !current)}
            aria-label={expanded ? "Collapse widget labels" : "Expand widget labels"}
            title={expanded ? "Collapse widget labels" : "Expand widget labels"}
            className={`flex h-10 w-full items-center rounded-lg border border-transparent text-white/40 transition-colors hover:border-white/10 hover:bg-white/[0.04] hover:text-white/75 ${
              expanded ? "justify-start gap-3 px-2.5" : "justify-center"
            }`}
          >
            {expanded ? <X size={18} strokeWidth={1.7} /> : <Plus size={18} strokeWidth={1.7} />}
            {expanded && <span className="text-[10px] font-semibold">Collapse labels</span>}
          </button>

          <button
            type="button"
            onClick={() => toggleWidget('system')}
            aria-label="Open system widget"
            aria-pressed={Boolean(widgetState.system?.visible)}
            title="Open system widget"
            className={`flex h-10 w-full items-center rounded-lg border transition-colors ${
              expanded ? "justify-start gap-3 px-2.5" : "justify-center"
            } ${
              widgetState.system?.visible
                ? `${activeBorder} ${activeBackground} ${activeText}`
                : "border-transparent text-white/40 hover:border-white/10 hover:bg-white/[0.04] hover:text-white/75"
            }`}
          >
            <Settings size={18} strokeWidth={1.7} aria-hidden="true" />
            {expanded && <span className="text-[10px] font-semibold">System widget</span>}
          </button>
        </div>
      </div>
    </aside>
  );
}
