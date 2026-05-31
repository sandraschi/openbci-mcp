import { Card } from "@/components/ui/card";

export function Chat() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">LLM Chat</h1>
      <Card>
        <p className="text-zinc-400">
          Connect your MCP client to <code className="text-cyan-300">http://127.0.0.1:10759/mcp</code> and use
          openbci_* tools from chat. Embedded host chat can be added when sampling is enabled.
        </p>
      </Card>
    </div>
  );
}
