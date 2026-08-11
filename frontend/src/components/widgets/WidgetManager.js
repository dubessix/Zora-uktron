import React, { lazy } from 'react';

// Lazy loading all widget components to optimize bundle footprint and render speed
const TodoWidget = lazy(() => import('./TodoWidget'));
const CalendarWidget = lazy(() => import('./CalendarWidget'));
const GitWidget = lazy(() => import('./GitWidget'));
const FileExplorerWidget = lazy(() => import('./FileExplorerWidget'));
const UniversalSearchWidget = lazy(() => import('./UniversalSearchWidget'));
const DeepResearchWidget = lazy(() => import('./DeepResearchWidget'));
const WeatherWidget = lazy(() => import('./WeatherWidget'));
const MarketWidget = lazy(() => import('./MarketWidget'));
const TerminalWidget = lazy(() => import('./TerminalWidget'));
const MemoryWidget = lazy(() => import('./MemoryWidget'));
const NotificationWidget = lazy(() => import('./NotificationWidget'));
const SystemWidget = lazy(() => import('./SystemWidget'));
const ReminderWidget = lazy(() => import('./ReminderWidget'));
const CodeOptimizerWidget = lazy(() => import('./CodeOptimizerWidget'));
const SemanticCodeGraphWidget = lazy(() => import('./SemanticCodeGraphWidget'));
const SecurityGuardianWidget = lazy(() => import('./SecurityGuardianWidget'));
const DailyBriefingWidget = lazy(() => import('./DailyBriefingWidget'));

/**
 * Standardized Frontend Widget Registry Map (OCP Compliant)
 * Every widget implements a common interface containing: id, title, category, default dimensions, and Component.
 * Enables dynamic registration, mounting, and destruction of widgets without altering the AppShell.
 */
export const WIDGET_REGISTRY = {
  todo: {
    id: "todo",
    title: "Daily Task Manager",
    category: "productivity",
    defaultWidth: 320,
    defaultHeight: 280,
    Component: TodoWidget
  },
  calendar: {
    id: "calendar",
    title: "Day Planner & Schedule",
    category: "productivity",
    defaultWidth: 320,
    defaultHeight: 240,
    Component: CalendarWidget
  },
  reminder: {
    id: "reminder",
    title: "Reminder & Alarm Core",
    category: "system",
    defaultWidth: 320,
    defaultHeight: 300,
    Component: ReminderWidget
  },
  code_optimizer: {
    id: "code_optimizer",
    title: "SOLID Code Optimizer",
    category: "system",
    defaultWidth: 320,
    defaultHeight: 300,
    Component: CodeOptimizerWidget
  },
  semantic_code_graph: {
    id: "semantic_code_graph",
    title: "Semantic Code Graph",
    category: "system",
    defaultWidth: 320,
    defaultHeight: 300,
    Component: SemanticCodeGraphWidget
  },
  security_guardian: {
    id: "security_guardian",
    title: "Security Guardian",
    category: "system",
    defaultWidth: 320,
    defaultHeight: 300,
    Component: SecurityGuardianWidget
  },
  daily_briefing: {
    id: "daily_briefing",
    title: "Daily Briefing Engine",
    category: "productivity",
    defaultWidth: 320,
    defaultHeight: 300,
    Component: DailyBriefingWidget
  },
  git: {
    id: "git",
    title: "Git Repository Watcher",
    category: "developer",
    defaultWidth: 320,
    defaultHeight: 300,
    Component: GitWidget
  },
  file_explorer: {
    id: "file_explorer",
    title: "Local File Explorer",
    category: "system",
    defaultWidth: 340,
    defaultHeight: 260,
    Component: FileExplorerWidget
  },
  universal_search: {
    id: "universal_search",
    title: "Universal search Engine",
    category: "system",
    defaultWidth: 320,
    defaultHeight: 260,
    Component: UniversalSearchWidget
  },
  deep_research: {
    id: "deep_research",
    title: "Deep AI Research",
    category: "research",
    defaultWidth: 320,
    defaultHeight: 280,
    Component: DeepResearchWidget
  },
  weather: {
    id: "weather",
    title: "Local Weather Watcher",
    category: "productivity",
    defaultWidth: 320,
    defaultHeight: 280,
    Component: WeatherWidget
  },
  market: {
    id: "market",
    title: "Live Market Index",
    category: "productivity",
    defaultWidth: 320,
    defaultHeight: 220,
    Component: MarketWidget
  },
  terminal: {
    id: "terminal",
    title: "Terminal Subprocess logs",
    category: "developer",
    defaultWidth: 340,
    defaultHeight: 240,
    Component: TerminalWidget
  },
  memory: {
    id: "memory",
    title: "Memory DB Viewer",
    category: "memory",
    defaultWidth: 320,
    defaultHeight: 280,
    Component: MemoryWidget
  },
  notification: {
    id: "notification",
    title: "System Notification Hub",
    category: "system",
    defaultWidth: 320,
    defaultHeight: 240,
    Component: NotificationWidget
  },
  system: {
    id: "system",
    title: "Hardware System Metrics",
    category: "system",
    defaultWidth: 320,
    defaultHeight: 280,
    Component: SystemWidget
  }
};
