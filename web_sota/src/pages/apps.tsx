import { Card } from "@/components/ui/card";

const FLEET_HINTS = [
  { name: "osc-mcp", port: 10766, note: "Route BCI triggers to VR/production" },
  { name: "obs-mcp", port: 10818, note: "Stream overlays during neurofeedback" },
  { name: "reaper-mcp", port: 10796, note: "Sonify band power in DAW" },
];

export function Apps() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Apps Hub</h1>
      <p className="text-zinc-400">
        Suggested fleet companions for BCI workflows. Full dynamic discovery can be wired to fleet
        registry.
      </p>
      <div className="grid gap-4 md:grid-cols-3">
        {FLEET_HINTS.map((a) => (
          <Card key={a.name}>
            <div className="font-mono text-violet-300">{a.name}</div>
            <div className="text-sm text-zinc-500">:{a.port}</div>
            <p className="mt-2 text-sm text-zinc-300">{a.note}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}
