import { Activity, Plug, Radio, Waves } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { fetchJson } from "@/lib/utils";
import { API_BASE } from "@/lib/api";

type BoardStatus = {
  connected?: boolean;
  streaming?: boolean;
  board_key?: string;
  serial_port?: string;
  sampling_rate?: number;
  num_eeg_channels?: number;
  eeg_channel_names?: string[];
};

type PortInfo = { device: string; description: string };

export function Dashboard() {
  const [status, setStatus] = useState<BoardStatus>({});
  const [ports, setPorts] = useState<PortInfo[]>([]);
  const [serialPort, setSerialPort] = useState("COM3");
  const [boardKey, setBoardKey] = useState("cyton");
  const [bands, setBands] = useState<Record<string, Record<string, number>>>({});
  const [error, setError] = useState<string | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const refresh = useCallback(async () => {
    try {
      const st = await fetchJson<BoardStatus>("/api/status");
      setStatus(st);
      const boards = await fetchJson<{ ports?: PortInfo[] }>("/api/boards");
      setPorts(boards.ports ?? []);
    } catch (e) {
      setError(String(e));
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const drawEeg = useCallback((channels: Record<string, number[]>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    const names = Object.keys(channels).slice(0, 4);
    const colors = ["#22d3ee", "#a78bfa", "#34d399", "#fbbf24"];
    names.forEach((name, idx) => {
      const data = channels[name] ?? [];
      if (data.length < 2) return;
      ctx.strokeStyle = colors[idx % colors.length];
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      const min = Math.min(...data);
      const max = Math.max(...data);
      const range = max - min || 1;
      const rowH = h / names.length;
      const yBase = rowH * idx + rowH / 2;
      data.forEach((v, i) => {
        const x = (i / (data.length - 1)) * w;
        const y = yBase - ((v - min) / range - 0.5) * (rowH * 0.8);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
      ctx.fillStyle = colors[idx % colors.length];
      ctx.font = "10px monospace";
      ctx.fillText(name, 4, rowH * idx + 12);
    });
  }, []);

  useEffect(() => {
    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${window.location.host}/api/ws/eeg`);
    wsRef.current = ws;
    ws.onmessage = (ev) => {
      const msg = JSON.parse(ev.data) as {
        type: string;
        snapshot?: { channels?: Record<string, number[]> };
        bands?: Record<string, Record<string, number>>;
      };
      if (msg.type === "frame" && msg.snapshot?.channels) {
        drawEeg(msg.snapshot.channels);
        if (msg.bands) setBands(msg.bands);
      }
    };
    ws.onerror = () => setError("WebSocket disconnected");
    return () => ws.close();
  }, [drawEeg]);

  const boardAction = async (operation: string, extra: Record<string, unknown> = {}) => {
    setError(null);
    try {
      const r = await fetch(API_BASE + "/api/board", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ operation, board_key: boardKey, serial_port: serialPort, ...extra }),
      });
      const j = (await r.json()) as { error?: string };
      if (j.error) setError(j.error);
      await refresh();
    } catch (e) {
      setError(String(e));
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold gradient-text">OpenBCI Dashboard</h1>
        <p className="text-zinc-400">Live EEG via BrainFlow · Cyton / Ganglion / synthetic</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card className="flex items-center gap-3">
          <Plug className="h-5 w-5 text-cyan-400" />
          <div>
            <div className="text-xs text-zinc-500">Connection</div>
            <div className="font-semibold">{status.connected ? "Connected" : "Idle"}</div>
          </div>
        </Card>
        <Card className="flex items-center gap-3">
          <Radio className="h-5 w-5 text-violet-400" />
          <div>
            <div className="text-xs text-zinc-500">Streaming</div>
            <div className="font-semibold">{status.streaming ? "Live" : "Stopped"}</div>
          </div>
        </Card>
        <Card className="flex items-center gap-3">
          <Waves className="h-5 w-5 text-emerald-400" />
          <div>
            <div className="text-xs text-zinc-500">Sample rate</div>
            <div className="font-semibold">{status.sampling_rate ?? 0} Hz</div>
          </div>
        </Card>
        <Card className="flex items-center gap-3">
          <Activity className="h-5 w-5 text-amber-400" />
          <div>
            <div className="text-xs text-zinc-500">Channels</div>
            <div className="font-semibold">{status.num_eeg_channels ?? 0}</div>
          </div>
        </Card>
      </div>

      <Card>
        <div className="mb-4 flex flex-wrap items-end gap-3">
          <label className="text-sm">
            Board
            <select
              className="ml-2 rounded bg-zinc-800 px-2 py-1"
              value={boardKey}
              onChange={(e) => setBoardKey(e.target.value)}
            >
              <option value="cyton">Cyton</option>
              <option value="ganglion">Ganglion</option>
              <option value="synthetic">Synthetic</option>
              <option value="streaming">Streaming (GUI)</option>
            </select>
          </label>
          <label className="text-sm">
            Serial
            <select
              className="ml-2 rounded bg-zinc-800 px-2 py-1"
              value={serialPort}
              onChange={(e) => setSerialPort(e.target.value)}
            >
              {[serialPort, ...ports.map((p) => p.device)]
                .filter((v, i, a) => a.indexOf(v) === i)
                .map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
            </select>
          </label>
          <Button onClick={() => void boardAction("connect")}>Connect</Button>
          <Button variant="ghost" onClick={() => void boardAction("disconnect")}>
            Disconnect
          </Button>
          <Button onClick={() => void boardAction("start_stream")}>Start stream</Button>
          <Button variant="ghost" onClick={() => void boardAction("stop_stream")}>
            Stop stream
          </Button>
        </div>
        {error && <p className="mb-2 text-sm text-red-400">{error}</p>}
        <canvas ref={canvasRef} className="eeg-canvas" width={900} height={180} />
      </Card>

      {Object.keys(bands).length > 0 && (
        <Card>
          <h2 className="mb-3 font-semibold">Band power</h2>
          <div className="grid gap-2 md:grid-cols-2">
            {Object.entries(bands).map(([ch, b]) => (
              <div key={ch} className="rounded-lg bg-zinc-900/80 p-3 text-xs font-mono">
                <div className="mb-1 font-sans font-medium text-cyan-300">{ch}</div>
                {Object.entries(b).map(([band, val]) => (
                  <div key={band} className="flex justify-between">
                    <span>{band}</span>
                    <span>{val.toExponential(2)}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
