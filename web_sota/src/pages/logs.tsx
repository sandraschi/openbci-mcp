import { ArrowDown, ArrowUp, Download, Radio, ScrollText, Trash2 } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  clearLogs,
  downloadLogsExport,
  getLogStats,
  type LogEntry,
  type LogQueryParams,
  type LogStats,
  queryLogs,
} from "@/lib/api";
import { cn } from "@/lib/utils";

const LEVELS = ["", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] as const;
const KINDS = ["", "board_action", "trigger", "server", "system", "tool_call"] as const;
const PAGE_SIZES = [25, 50, 100, 200] as const;

function levelTone(level: string): string {
  const l = level.toUpperCase();
  if (l === "ERROR" || l === "CRITICAL") return "text-rose-400 bg-rose-500/10 border-rose-500/30";
  if (l === "WARNING") return "text-amber-400 bg-amber-500/10 border-amber-500/30";
  if (l === "INFO") return "text-sky-400 bg-sky-500/10 border-sky-500/30";
  if (l === "DEBUG") return "text-slate-400 bg-slate-500/10 border-slate-500/30";
  return "text-slate-400 bg-zinc-800/50 border-zinc-700";
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export function Logs() {
  const [entries, setEntries] = useState<LogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [maxEntries, setMaxEntries] = useState(2000);
  const [stats, setStats] = useState<LogStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [pageSize, setPageSize] = useState(50);
  const [page, setPage] = useState(0);
  const [level, setLevel] = useState("");
  const [kind, setKind] = useState("");
  const [search, setSearch] = useState("");
  const [searchDraft, setSearchDraft] = useState("");
  const [sort, setSort] = useState<"asc" | "desc">("desc");
  const [liveTail, setLiveTail] = useState(true);
  const [autoScroll, setAutoScroll] = useState(true);

  const streamRef = useRef<HTMLDivElement>(null);
  const newestIdRef = useRef<string | null>(null);
  const userScrolledRef = useRef(false);

  const queryParams = useCallback((): LogQueryParams => {
    const base: LogQueryParams = { limit: pageSize, offset: page * pageSize, sort };
    if (level) base.level = level;
    if (kind) base.kind = kind;
    if (search.trim()) base.search = search.trim();
    return base;
  }, [page, pageSize, level, kind, search, sort]);

  const load = useCallback(async () => {
    try {
      const [logsRes, statsRes] = await Promise.all([queryLogs(queryParams()), getLogStats()]);
      setEntries(logsRes.entries);
      setTotal(logsRes.total);
      setMaxEntries(logsRes.max_entries);
      if (logsRes.entries.length > 0 && sort === "desc") {
        newestIdRef.current = logsRes.entries[0].id;
      }
      setStats(statsRes);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load logs");
    } finally {
      setLoading(false);
    }
  }, [queryParams, sort]);

  const tailPoll = useCallback(async () => {
    if (!liveTail || page !== 0 || sort !== "desc") return;
    try {
      const params = queryParams();
      params.limit = pageSize;
      params.offset = 0;
      if (newestIdRef.current) params.after_id = newestIdRef.current;
      const res = await queryLogs(params);
      if (res.entries.length === 0) return;
      newestIdRef.current = res.entries[0].id;
      setEntries((prev) => {
        const merged = [...res.entries, ...prev];
        const seen = new Set<string>();
        const deduped: LogEntry[] = [];
        for (const row of merged) {
          if (seen.has(row.id)) continue;
          seen.add(row.id);
          deduped.push(row);
        }
        return deduped.slice(0, pageSize);
      });
      setTotal((t) => t + res.entries.length);
    } catch {
      /* tail errors are non-fatal */
    }
  }, [liveTail, page, pageSize, queryParams, sort]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (!liveTail) return undefined;
    const id = window.setInterval(() => {
      void tailPoll();
    }, 1500);
    return () => window.clearInterval(id);
  }, [liveTail, tailPoll]);

  // biome-ignore lint/correctness/useExhaustiveDependencies: scroll when log stream updates
  useEffect(() => {
    const el = streamRef.current;
    if (!el || !autoScroll || userScrolledRef.current) return;
    el.scrollTop = sort === "desc" ? 0 : el.scrollHeight;
  }, [entries.length, autoScroll, sort]);

  const onStreamScroll = () => {
    const el = streamRef.current;
    if (!el) return;
    const atTop = el.scrollTop < 48;
    userScrolledRef.current = !atTop;
    if (atTop) setAutoScroll(true);
  };

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const handleExport = async (format: "json" | "csv") => {
    await downloadLogsExport(format, {
      level: level || undefined,
      kind: kind || undefined,
      search: search.trim() || undefined,
      sort,
    });
  };

  const handleClear = async () => {
    if (!window.confirm("Clear all in-memory log entries?")) return;
    await clearLogs();
    newestIdRef.current = null;
    setPage(0);
    await load();
  };

  const selectClass =
    "w-full rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100";

  return (
    <div className="space-y-6 page-enter">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="flex items-center gap-2 text-cyan-400">
            <ScrollText className="h-6 w-6" />
            <span className="text-sm font-medium uppercase tracking-wider">Operations</span>
          </div>
          <h2 className="mt-1 text-3xl font-bold tracking-tight">Event logs</h2>
          <p className="text-zinc-400">
            Board actions, triggers, and server events - ring buffer with live tail
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant="ghost"
            className="border border-zinc-700"
            onClick={() => void handleExport("json")}
          >
            <Download className="mr-2 h-4 w-4" />
            JSON
          </Button>
          <Button
            variant="ghost"
            className="border border-zinc-700"
            onClick={() => void handleExport("csv")}
          >
            <Download className="mr-2 h-4 w-4" />
            CSV
          </Button>
          <Button variant="danger" onClick={() => void handleClear()}>
            <Trash2 className="mr-2 h-4 w-4" />
            Clear
          </Button>
        </div>
      </div>

      {stats && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { label: "Buffered", value: stats.total.toLocaleString() },
            { label: "Capacity", value: stats.max_entries.toLocaleString() },
            {
              label: "Errors",
              value: (
                (stats.by_level.ERROR ?? 0) + (stats.by_level.CRITICAL ?? 0)
              ).toLocaleString(),
            },
            { label: "Board actions", value: (stats.by_kind.board_action ?? 0).toLocaleString() },
          ].map((item) => (
            <Card key={item.label} className="border-zinc-800 bg-zinc-950/80">
              <p className="text-xs uppercase tracking-wide text-zinc-500">{item.label}</p>
              <p className="text-2xl font-semibold">{item.value}</p>
            </Card>
          ))}
        </div>
      )}

      <Card className="border-zinc-800 bg-zinc-950/60">
        <h3 className="mb-1 text-lg font-semibold">Filters</h3>
        <p className="mb-4 text-sm text-zinc-500">Search, filter, paginate - live tail on page 1</p>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6">
          <div className="space-y-1.5">
            <label className="text-sm text-zinc-400" htmlFor="log-search">
              Search
            </label>
            <input
              id="log-search"
              placeholder="tool name, error..."
              value={searchDraft}
              onChange={(e) => setSearchDraft(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  setSearch(searchDraft);
                  setPage(0);
                }
              }}
              className={selectClass}
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm text-zinc-400" htmlFor="log-level">
              Level
            </label>
            <select
              id="log-level"
              value={level}
              onChange={(e) => {
                setLevel(e.target.value);
                setPage(0);
              }}
              className={selectClass}
            >
              <option value="">All levels</option>
              {LEVELS.filter(Boolean).map((lv) => (
                <option key={lv} value={lv}>
                  {lv}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-1.5">
            <label className="text-sm text-zinc-400" htmlFor="log-kind">
              Kind
            </label>
            <select
              id="log-kind"
              value={kind}
              onChange={(e) => {
                setKind(e.target.value);
                setPage(0);
              }}
              className={selectClass}
            >
              <option value="">All kinds</option>
              {KINDS.filter(Boolean).map((k) => (
                <option key={k} value={k}>
                  {k}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-1.5">
            <label className="text-sm text-zinc-400" htmlFor="log-page-size">
              Page size
            </label>
            <select
              id="log-page-size"
              value={String(pageSize)}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setPage(0);
              }}
              className={selectClass}
            >
              {PAGE_SIZES.map((n) => (
                <option key={n} value={String(n)}>
                  {n} rows
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-1.5">
            <span className="text-sm text-zinc-400">Sort</span>
            <Button
              variant="ghost"
              className="w-full justify-between border border-zinc-700"
              onClick={() => {
                setSort((s) => (s === "desc" ? "asc" : "desc"));
                setPage(0);
              }}
            >
              {sort === "desc" ? "Newest first" : "Oldest first"}
              {sort === "desc" ? (
                <ArrowDown className="h-4 w-4" />
              ) : (
                <ArrowUp className="h-4 w-4" />
              )}
            </Button>
          </div>
          <div className="flex items-end gap-2 pb-0.5">
            <input
              id="live-tail"
              type="checkbox"
              checked={liveTail}
              onChange={(e) => setLiveTail(e.target.checked)}
              className="h-4 w-4"
            />
            <label
              htmlFor="live-tail"
              className="flex cursor-pointer items-center gap-1.5 text-zinc-300"
            >
              <Radio className={cn("h-4 w-4", liveTail ? "text-emerald-400" : "text-zinc-600")} />
              Live tail
            </label>
          </div>
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <Button
            onClick={() => {
              setSearch(searchDraft);
              setPage(0);
              void load();
            }}
          >
            Apply filters
          </Button>
          <Button
            variant="ghost"
            onClick={() => {
              setSearchDraft("");
              setSearch("");
              setLevel("");
              setKind("");
              setPage(0);
            }}
          >
            Reset
          </Button>
        </div>
      </Card>

      <Card className="overflow-hidden border-zinc-800 bg-zinc-950/80 p-0">
        <div className="flex flex-row items-center justify-between border-b border-zinc-800 px-4 py-3">
          <div>
            <h3 className="text-base font-semibold">Log stream</h3>
            <p className="text-xs text-zinc-500">
              {total.toLocaleString()} matching - max {maxEntries.toLocaleString()} retained
              {liveTail && page === 0 && <span className="ml-2 text-emerald-400">tail active</span>}
            </p>
          </div>
        </div>
        {error && (
          <p className="border-b border-rose-900/50 bg-rose-950/30 px-4 py-2 text-sm text-rose-300">
            {error}
          </p>
        )}
        <div
          ref={streamRef}
          onScroll={onStreamScroll}
          className="max-h-[min(58vh,520px)] overflow-y-auto font-mono text-xs leading-relaxed"
        >
          {loading && entries.length === 0 ? (
            <p className="p-6 text-zinc-500">Loading logs...</p>
          ) : entries.length === 0 ? (
            <p className="p-6 text-zinc-500">No entries match your filters.</p>
          ) : (
            entries.map((entry) => (
              <div
                key={entry.id}
                className="grid grid-cols-[auto_auto_1fr] gap-x-3 border-b border-zinc-800/80 px-4 py-2 hover:bg-zinc-900/60"
              >
                <time className="whitespace-nowrap text-zinc-500">
                  {formatTime(entry.timestamp)}
                </time>
                <span
                  className={cn(
                    "rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase",
                    levelTone(entry.level),
                  )}
                >
                  {entry.level}
                </span>
                <div className="min-w-0 text-zinc-200">
                  <span className="text-violet-400">[{entry.kind}]</span> {entry.detail}
                  {entry.meta && Object.keys(entry.meta).length > 0 && (
                    <span className="mt-0.5 block truncate text-zinc-500">
                      {JSON.stringify(entry.meta)}
                    </span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
        <div className="flex flex-wrap items-center justify-between gap-2 border-t border-zinc-800 px-4 py-3 text-sm text-zinc-400">
          <span>
            Page {page + 1} of {totalPages}
          </span>
          <div className="flex gap-2">
            <Button
              variant="ghost"
              className="border border-zinc-700"
              disabled={page <= 0}
              onClick={() => setPage((p) => Math.max(0, p - 1))}
            >
              Previous
            </Button>
            <Button
              variant="ghost"
              className="border border-zinc-700"
              disabled={page + 1 >= totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
