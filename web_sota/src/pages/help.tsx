import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { fetchJson } from "@/lib/utils";

type HelpIndex = {
  docs?: string[];
  labels?: Record<string, string>;
  webapp_port?: number;
  backend_port?: number;
};

type HelpDoc = {
  markdown?: string;
  title?: string;
  error?: string;
};

const DEFAULT_DOC = "overview";

export function Help() {
  const [index, setIndex] = useState<HelpIndex>({});
  const [active, setActive] = useState(DEFAULT_DOC);
  const [markdown, setMarkdown] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void fetchJson<HelpIndex>("/api/help")
      .then(setIndex)
      .catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    setError(null);
    void fetchJson<HelpDoc>(`/api/help/${active}`)
      .then((doc) => {
        if (doc.error) {
          setError(doc.error);
          setMarkdown("");
          return;
        }
        setMarkdown(doc.markdown ?? "");
      })
      .catch((e) => setError(String(e)));
  }, [active]);

  const docs = index.docs ?? [];

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold gradient-text">Help</h1>
        <p className="text-zinc-400">
          Docs from <code className="text-cyan-300">/api/help</code> · UI port{" "}
          <span className="font-mono">{index.webapp_port ?? 10758}</span> · API port{" "}
          <span className="font-mono">{index.backend_port ?? 10759}</span>
        </p>
      </div>

      {error && (
        <Card className="border-red-900/50 text-red-300">
          <p className="text-sm">{error}</p>
          <p className="mt-2 text-xs text-zinc-500">
            If API calls fail, start the backend:{" "}
            <code className="text-zinc-300">uv run openbci-mcp --serve</code>
          </p>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-[220px_1fr]">
        <Card className="space-y-1 p-2">
          {docs.map((id) => (
            <button
              key={id}
              type="button"
              className={`block w-full rounded-lg px-3 py-2 text-left text-sm ${
                active === id ? "bg-cyan-950/60 text-cyan-200" : "text-zinc-400 hover:bg-zinc-800"
              }`}
              onClick={() => setActive(id)}
            >
              {index.labels?.[id] ?? id}
            </button>
          ))}
        </Card>
        <Card>
          <pre className="max-h-[70vh] overflow-auto whitespace-pre-wrap text-sm text-zinc-300">
            {markdown || "Loading..."}
          </pre>
        </Card>
      </div>
    </div>
  );
}
