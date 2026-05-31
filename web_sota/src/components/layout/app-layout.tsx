import { useState, type ReactNode } from "react";
import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

export function AppLayout({ children }: { children: ReactNode }) {
  const [collapsed] = useState(false);
  return (
    <div className="flex min-h-screen bg-zinc-950 text-zinc-50">
      <Sidebar collapsed={collapsed} />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="mx-auto max-w-6xl page-enter">{children}</div>
        </main>
      </div>
    </div>
  );
}
