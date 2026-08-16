import React, { useState } from 'react';
import useDraggable from '../../hooks/useDraggable';
import { getPersonalityTheme } from '../../theme/personalityTheme';

/**
 * WidgetContainer Component
 * Renders a draggable, collapsible glassmorphic wrapper modal.
 * Uses useDraggable hook for pointer tracking, supports double-click collapse states,
 * and configures active personality-based neon border accents.
 */
export default function WidgetContainer({ 
  widgetId,
  title, 
  onClose, 
  initialX = 150, 
  initialY = 150, 
  initialWidth = 320,
  initialHeight = 280,
  personality = "ultron", 
  children 
}) {
  const { position, handleMouseDown, isDragging } = useDraggable(initialX, initialY);
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Map active colors dynamically from the shared personality contract.
  const theme = getPersonalityTheme(personality);

  // Double-click header bar to toggle collapsed/expanded states (Requirement: remember collapsed state)
  const handleHeaderDoubleClick = () => {
    setIsCollapsed(!isCollapsed);
    console.log(`[WIDGET_CONTAINER] Widget '${widgetId}' collapsed state set to: ${!isCollapsed}`);
  };

  return (
    <div 
      style={{
        transform: `translate3d(${position.x}px, ${position.y}px, 0)`,
        position: 'absolute',
        zIndex: isDragging ? 1000 : 50,
        width: `${initialWidth}px`,
        height: isCollapsed ? 'auto' : `${initialHeight}px`,
        borderLeftColor: theme.primary,
        boxShadow: `0 0 20px ${theme.glow}`,
      }}
      className="bg-[#14141E]/85 border border-white/5 border-l-[3px] rounded-lg backdrop-blur-2xl flex flex-col overflow-hidden select-none cursor-default font-mono transition-shadow duration-300"
    >
      {/* Draggable Header Drag Bar */}
      <div 
        onMouseDown={handleMouseDown}
        onDoubleClick={handleHeaderDoubleClick}
        className="flex justify-between items-center bg-white/[0.02] border-b border-white/5 px-4 py-2.5 cursor-grab active:cursor-grabbing text-[#8B8B96]"
        title="Drag header to move. Double-click to collapse/expand."
      >
        <span className="text-[9px] uppercase font-bold tracking-widest text-[#F5F5F7]">
          {title} {isCollapsed && "(Collapsed)"}
        </span>
        <button 
          onClick={onClose}
          className="no-drag text-[9px] text-[#8B8B96] hover:text-rose-400 uppercase tracking-widest transition-colors"
        >
          Close
        </button>
      </div>

      {/* Embedded Inner Children Viewport (Lazy rendered/hidden on collapse) */}
      {!isCollapsed && (
        <div className="p-4 flex-1 overflow-y-auto max-h-60 scrollbar-thin select-text">
          {children}
        </div>
      )}
    </div>
  );
}
