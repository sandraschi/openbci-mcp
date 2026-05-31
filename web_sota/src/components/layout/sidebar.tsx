import { BookOpen, Brain, HelpCircle, LayoutDashboard, MessageSquare, Network, Wrench, Zap } from "lucide-react";
import { NavLink } from "react-router-dom";
import { cn } from "@/lib/utils";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/triggers", label: "Triggers", icon: Zap },
  { to: "/tools", label: "Tools", icon: Wrench },
  { to: "/apps", label: "Apps", icon: Network },
  { to: "/chat", label: "Chat", icon: MessageSquare },
  { to: "/status", label: "Status", icon: Brain },
  { to: "/help", label: "Help", icon: HelpCircle },
  { to: "/skill", label: "Skill", icon: BookOpen },
];

export function Sidebar({ collapsed }: { collapsed: boolean }) {
  return (
    <aside
      className={cn(
        "flex flex-col border-r border-zinc-800 bg-zinc-950/90 p-3 transition-all",
        collapsed ? "w-16" : "w-56",
      )}
    >
      <div className="mb-6 flex items-center gap-2 px-2">
        <Brain className="h-6 w-6 text-cyan-400" />
        {!collapsed && (
          <div>
            <div className="text-sm font-bold">openbci-mcp</div>
            <div className="text-xs text-zinc-500">v0.1.0</div>
          </div>
        )}
      </div>
      <nav className="flex flex-1 flex-col gap-1">
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition",
                isActive ? "bg-cyan-950/50 text-cyan-300" : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100",
              )
            }
          >
            <Icon className="h-4 w-4 shrink-0" />
            {!collapsed && label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
