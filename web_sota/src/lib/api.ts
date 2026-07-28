/**
 * REST bridge to openbci-mcp backend (proxied via Vite in dev).
 */

export interface LogEntry {
  id: string;
  timestamp: string;
  level: string;
  kind: string;
  detail: string;
  meta?: Record<string, unknown>;
}

export interface LogsQueryResponse {
  entries: LogEntry[];
  total: number;
  limit: number;
  offset: number;
  max_entries: number;
  sort: string;
}

export interface LogStats {
  total: number;
  max_entries: number;
  rotation: string;
  by_level: Record<string, number>;
  by_kind: Record<string, number>;
  oldest: string | null;
  newest: string | null;
}

export interface LogQueryParams {
  limit?: number;
  offset?: number;
  level?: string;
  kind?: string;
  search?: string;
  sort?: "asc" | "desc";
  after_id?: string;
}

export interface LlmSettings {
  provider: string;
  model: string;
  endpoint: string;
}

export interface LlmProvider {
  type: string;
  label: string;
  base_url: string;
  models: string[];
  reachable: boolean;
  needs_key: boolean;
}

export interface AiChatRequest {
  message: string;
  provider?: string;
  model?: string;
  endpoint?: string;
}

export interface AiChatResponse {
  response: string;
  tool_calls?: string[];
}

export const API_BASE = "http://127.0.0.1:10759";
const API = API_BASE + "/api";
const LLM_KEY = "openbci-llm-settings";
const OSC_KEY = "openbci-osc-settings";

export interface OscSettings {
  host: string;
  port: number;
}

export function getLlmSettings(): LlmSettings {
  try {
    const raw = localStorage.getItem(LLM_KEY);
    if (raw) return JSON.parse(raw) as LlmSettings;
  } catch {
    /* ignore */
  }
  return {
    provider: "ollama",
    model: "llama3.2",
    endpoint: "http://127.0.0.1:11434",
  };
}

export function setLlmSettings(settings: LlmSettings): void {
  localStorage.setItem(LLM_KEY, JSON.stringify(settings));
}

export function getOscSettings(): OscSettings {
  try {
    const raw = localStorage.getItem(OSC_KEY);
    if (raw) return JSON.parse(raw) as OscSettings;
  } catch {
    /* ignore */
  }
  return { host: "127.0.0.1", port: 9000 };
}

export function setOscSettings(settings: OscSettings): void {
  localStorage.setItem(OSC_KEY, JSON.stringify(settings));
}

function buildLogParams(params: LogQueryParams): string {
  const q = new URLSearchParams();
  if (params.limit != null) q.set("limit", String(params.limit));
  if (params.offset != null) q.set("offset", String(params.offset));
  if (params.level) q.set("level", params.level);
  if (params.kind) q.set("kind", params.kind);
  if (params.search) q.set("search", params.search);
  if (params.sort) q.set("sort", params.sort);
  if (params.after_id) q.set("after_id", params.after_id);
  return q.toString();
}

export async function queryLogs(params: LogQueryParams = {}): Promise<LogsQueryResponse> {
  const qs = buildLogParams(params);
  const r = await fetch(`${API}/logs${qs ? `?${qs}` : ""}`);
  if (!r.ok) throw new Error(`Logs query failed: ${r.status}`);
  return r.json();
}

export async function getLogStats(): Promise<LogStats> {
  const r = await fetch(`${API}/logs/stats`);
  if (!r.ok) throw new Error(`Log stats failed: ${r.status}`);
  return r.json();
}

export async function clearLogs(): Promise<void> {
  const r = await fetch(`${API}/logs`, { method: "DELETE" });
  if (!r.ok) throw new Error(`Clear logs failed: ${r.status}`);
}

export async function downloadLogsExport(
  format: "json" | "csv",
  filters: Omit<LogQueryParams, "limit" | "offset" | "after_id"> = {},
): Promise<void> {
  const q = buildLogParams({ ...filters, limit: undefined, offset: undefined });
  const r = await fetch(`${API}/logs/export?format=${format}${q ? `&${q}` : ""}`);
  if (!r.ok) throw new Error(`Export failed: ${r.status}`);
  const blob = await r.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `openbci-mcp-logs.${format}`;
  anchor.click();
  URL.revokeObjectURL(url);
}

export async function getLlmProviders(): Promise<LlmProvider[]> {
  const r = await fetch(`${API}/llm/providers`);
  if (!r.ok) throw new Error(`LLM providers failed: ${r.status}`);
  const body = await r.json();
  return body.providers ?? [];
}

export async function postAiChat(body: AiChatRequest): Promise<AiChatResponse> {
  const r = await fetch(`${API}/ai/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const text = await r.text();
    throw new Error(text || `AI chat failed: ${r.status}`);
  }
  return r.json();
}

export async function getHealth(): Promise<Record<string, unknown>> {
  const r = await fetch("/health");
  if (!r.ok) throw new Error(`Health check failed: ${r.status}`);
  return r.json();
}
