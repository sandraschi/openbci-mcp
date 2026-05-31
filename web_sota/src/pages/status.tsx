import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { fetchJson } from "@/lib/utils";

export function Status() {
  const [health, setHealth] = useState<Record<string, unknown> | null>(null);
  const [status, setStatus] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    const tick = () => {
      void fetchJson<Record<string, unknown>>("/health").then(setHealth);
      void fetchJson<Record<string, unknown>>("/api/status").then(setStatus);
    };
    tick();
    const id = setInterval(tick, 5000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Status / Audit</h1>
      <Card>
        <h2 className="mb-2 font-semibold">Health</h2>
        <pre className="overflow-auto text-xs text-zinc-300">{JSON.stringify(health, null, 2)}</pre>
      </Card>
      <Card>
        <h2 className="mb-2 font-semibold">Board</h2>
        <pre className="overflow-auto text-xs text-zinc-300">{JSON.stringify(status, null, 2)}</pre>
      </Card>
    </div>
  );
}
