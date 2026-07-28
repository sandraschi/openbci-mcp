import { Cpu, RefreshCw, Save, Settings2, Zap } from "lucide-react";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  getHealth,
  getLlmProviders,
  getLlmSettings,
  getOscSettings,
  type LlmProvider,
  setLlmSettings,
  setOscSettings,
} from "@/lib/api";

export function Settings() {
  const [provider, setProvider] = useState(() => getLlmSettings().provider);
  const [model, setModel] = useState(() => getLlmSettings().model);
  const [endpoint, setEndpoint] = useState(() => getLlmSettings().endpoint);
  const [oscHost, setOscHost] = useState(() => getOscSettings().host);
  const [oscPort, setOscPort] = useState(() => String(getOscSettings().port));
  const [glomProviders, setGlomProviders] = useState<LlmProvider[]>([]);
  const [apiStatus, setApiStatus] = useState<string | null>(null);

  const inputClass =
    "w-full rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100";

  useEffect(() => {
    void getLlmProviders()
      .then(setGlomProviders)
      .catch(() => setGlomProviders([]));
  }, []);

  const testApi = async () => {
    setApiStatus("Testing...");
    try {
      await getHealth();
      setApiStatus("API reachable on port 10759");
    } catch (err) {
      setApiStatus(err instanceof Error ? err.message : "API test failed");
    }
  };

  const refreshGlom = async () => {
    setApiStatus("Refreshing local LLM discovery...");
    try {
      const providers = await getLlmProviders();
      setGlomProviders(providers);
      if (providers.length === 0) {
        setApiStatus("No local LLM found (Ollama :11434, LM Studio :1234)");
        return;
      }
      const first = providers[0];
      setProvider(first.type);
      setEndpoint(first.base_url);
      if (first.models[0]) setModel(first.models[0]);
      setApiStatus(`Glom on: ${providers.map((p) => p.type).join(", ")}`);
    } catch (err) {
      setApiStatus(err instanceof Error ? err.message : "Glom refresh failed");
    }
  };

  return (
    <div className="space-y-6 page-enter">
      <div>
        <div className="flex items-center gap-2 text-cyan-400">
          <Settings2 className="h-6 w-6" />
          <span className="text-sm font-medium uppercase tracking-wider">Configuration</span>
        </div>
        <h2 className="mt-1 text-3xl font-bold tracking-tight">Settings</h2>
        <p className="text-zinc-400">OSC defaults, API health, and local LLM glom-on preferences</p>
      </div>

      <Card className="border-zinc-800 bg-zinc-950/50">
        <h3 className="mb-1 flex items-center gap-2 text-lg font-semibold">
          <Zap className="h-5 w-5 text-amber-400" />
          OSC / triggers
        </h3>
        <p className="mb-4 text-sm text-zinc-500">
          Default destination for trigger rules (stored locally)
        </p>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-1.5">
            <label className="text-sm text-zinc-400" htmlFor="osc-host">
              OSC host
            </label>
            <input
              id="osc-host"
              value={oscHost}
              onChange={(e) => setOscHost(e.target.value)}
              className={inputClass}
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm text-zinc-400" htmlFor="osc-port">
              OSC port
            </label>
            <input
              id="osc-port"
              type="number"
              value={oscPort}
              onChange={(e) => setOscPort(e.target.value)}
              className={inputClass}
            />
          </div>
        </div>
        <Button
          className="mt-4"
          onClick={() => {
            setOscSettings({ host: oscHost, port: Number(oscPort) || 9000 });
            setApiStatus("OSC settings saved locally");
          }}
        >
          <Save className="mr-2 h-4 w-4" />
          Save OSC settings
        </Button>
      </Card>

      <Card className="border-zinc-800 bg-zinc-950/50">
        <h3 className="mb-1 flex items-center gap-2 text-lg font-semibold">
          <Cpu className="h-5 w-5 text-cyan-400" />
          Local LLM (Glom On)
        </h3>
        <p className="mb-4 text-sm text-zinc-500">
          Backend probes Ollama (11434) and LM Studio (1234) on startup. Used by Chat page.
        </p>
        {glomProviders.length > 0 ? (
          <ul className="mb-4 space-y-1 text-sm text-emerald-300">
            {glomProviders.map((p) => (
              <li key={p.type}>
                {p.type} at {p.base_url}
                {p.models.length > 0 ? ` - ${p.models.slice(0, 3).join(", ")}` : ""}
              </li>
            ))}
          </ul>
        ) : (
          <p className="mb-4 text-sm text-zinc-500">
            No providers discovered yet. Start Ollama or LM Studio.
          </p>
        )}
        <div className="grid gap-4 md:grid-cols-3">
          <div className="space-y-1.5">
            <label className="text-sm text-zinc-400" htmlFor="llm-provider">
              Provider
            </label>
            <select
              id="llm-provider"
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className={inputClass}
            >
              {glomProviders.length > 0 ? (
                glomProviders.map((p) => (
                  <option key={p.type} value={p.type}>{p.label || p.type}</option>
                ))
              ) : (
                <>
                  <option value="ollama">Ollama</option>
                  <option value="lmstudio">LM Studio</option>
                </>
              )}
            </select>
          </div>
          <div className="space-y-1.5">
            <label className="text-sm text-zinc-400" htmlFor="llm-endpoint">
              API endpoint
            </label>
            <input
              id="llm-endpoint"
              value={endpoint}
              onChange={(e) => setEndpoint(e.target.value)}
              className={inputClass}
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-sm text-zinc-400" htmlFor="llm-model">
              Model
            </label>
            <input
              id="llm-model"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className={inputClass}
            />
          </div>
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <Button
            onClick={() => {
              setLlmSettings({ provider, model, endpoint });
              setApiStatus("LLM settings saved locally");
            }}
          >
            <Save className="mr-2 h-4 w-4" />
            Save LLM settings
          </Button>
          <Button
            variant="ghost"
            className="border border-zinc-700"
            onClick={() => void refreshGlom()}
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh glom
          </Button>
          <Button variant="ghost" className="border border-zinc-700" onClick={() => void testApi()}>
            Test API
          </Button>
        </div>
      </Card>

      <Card className="border-zinc-800 bg-zinc-950/50">
        <h3 className="mb-2 text-lg font-semibold">App information</h3>
        <div className="space-y-1 text-sm text-zinc-400">
          <p>openbci-mcp v0.1.0</p>
          <p>Frontend: 10758 - Backend: 10759</p>
          <p>MCP HTTP + BrainFlow EEG/EMG acquisition</p>
        </div>
      </Card>

      {apiStatus && <p className="text-sm text-zinc-400">{apiStatus}</p>}
    </div>
  );
}
