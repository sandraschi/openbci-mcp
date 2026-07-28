import { ChevronUp, Trash2 } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { useLogger } from "@/context/LoggerContext";
import { cn } from "@/lib/utils";

export function LoggerPanel() {
  const { entries, clear } = useLogger();
  const [open, setOpen] = useState(false);
  const [paused, setPaused] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  // biome-ignore lint/correctness/useExhaustiveDependencies: scroll when new log lines arrive
  useEffect(() => {
    if (!open || paused) return;
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [entries.length, open, paused]);

  return (
    <div
      className={cn(
        "fixed bottom-0 left-0 right-0 z-40 border-t border-zinc-800 bg-zinc-950/95 backdrop-blur-md transition-all md:pl-56",
        !open && "h-10",
      )}
    >
      <div className="flex h-10 items-center justify-between border-b border-zinc-800/50 px-3">
        <button
          type="button"
          className="flex items-center gap-1 text-xs font-medium text-zinc-400 hover:text-zinc-100"
          onClick={() => setOpen(!open)}
        >
          <ChevronUp className={cn("h-4 w-4 transition-transform", open && "rotate-180")} />
          Logger ({entries.length})
        </button>
        <div className="flex gap-1">
          <Button variant="ghost" className="h-7 px-2 text-xs" onClick={() => setPaused(!paused)}>
            {paused ? "Resume" : "Pause"}
          </Button>
          <Button variant="ghost" className="h-7 w-7 p-0" onClick={clear} aria-label="Clear logs">
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>
      {open && (
        <div
          className="h-48 space-y-1 overflow-y-auto px-3 py-2 font-mono text-[11px]"
          onScroll={(e) => {
            const el = e.currentTarget;
            const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 40;
            if (!atBottom) setPaused(true);
          }}
        >
          {entries.map((e) => (
            <div key={e.id} className="flex gap-2 opacity-90">
              <span className="shrink-0 text-zinc-500">{e.ts.slice(11, 19)}</span>
              <span
                className={cn(
                  "w-12 shrink-0 uppercase",
                  e.level === "error" && "text-red-400",
                  e.level === "warn" && "text-amber-400",
                  e.level === "debug" && "text-slate-400",
                )}
              >
                {e.level}
              </span>
              <span className="break-all">{e.message}</span>
            </div>
          ))}
          <div ref={endRef} />
        </div>
      )}
    </div>
  );
}
