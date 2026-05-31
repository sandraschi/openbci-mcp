export function Topbar() {
  return (
    <header className="flex h-14 items-center justify-between border-b border-zinc-800 bg-zinc-950/80 px-6">
      <div className="text-sm text-zinc-400">
        BrainFlow EEG · ports <span className="font-mono text-zinc-300">10758/10759</span>
      </div>
      <div className="flex items-center gap-2 text-xs text-zinc-500">
        <span className="inline-block h-2 w-2 rounded-full bg-emerald-500" />
        MCP HTTP /mcp
      </div>
    </header>
  );
}
