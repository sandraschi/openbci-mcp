import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { fetchJson } from "@/lib/utils";

type ToolEntry = {
  name: string;
  type: string;
  operations: string[];
};

export function Tools() {
  const [tools, setTools] = useState<ToolEntry[]>([]);

  useEffect(() => {
    void fetchJson<{ tools: ToolEntry[] }>("/api/tools").then((r) => setTools(r.tools ?? []));
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Tools Hub</h1>
      <p className="text-zinc-400">Portmanteau MCP tools registered on this server.</p>
      <div className="grid gap-4 md:grid-cols-2">
        {tools.map((t) => (
          <Card key={t.name}>
            <div className="mb-2 font-mono text-cyan-300">{t.name}</div>
            <div className="mb-2 text-xs uppercase tracking-wide text-zinc-500">{t.type}</div>
            <div className="flex flex-wrap gap-1">
              {t.operations.map((op) => (
                <span key={op} className="rounded bg-zinc-800 px-2 py-0.5 text-xs font-mono">
                  {op}
                </span>
              ))}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
