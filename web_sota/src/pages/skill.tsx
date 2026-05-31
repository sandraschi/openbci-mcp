import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { fetchJson } from "@/lib/utils";

export function Skill() {
  const [skill, setSkill] = useState("");

  useEffect(() => {
    void fetchJson<{ skill?: string }>("/api/skill").then((r) => setSkill(r.skill ?? ""));
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Skill</h1>
      <Card>
        <pre className="whitespace-pre-wrap text-sm text-zinc-300">{skill || "Loading skill..."}</pre>
      </Card>
    </div>
  );
}
