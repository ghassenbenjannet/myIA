import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { ArtifactRenderer } from "@/components/artifacts/artifact-renderer";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { shadowPoApi } from "@/lib/api/shadow-po-api";
import { useWorkspaceStore } from "@/stores/workspace-store";

export function ProcessForm() {
  const rememberRun = useWorkspaceStore((state) => state.rememberRun);
  const [userInput, setUserInput] = useState("");
  const [contextHint, setContextHint] = useState("");
  const [targetOutput, setTargetOutput] = useState("auto");

  const mutation = useMutation({
    mutationFn: shadowPoApi.process,
    onSuccess: (payload) => {
      rememberRun({
        runId: payload.run_id,
        topicId: payload.topic_id,
        workflow: payload.selected_workflow,
        label: payload.selected_workflow,
      });
    },
  });

  return (
    <div className="grid gap-5">
      <Card>
        <CardContent className="space-y-5">
          <div>
            <p className="text-xs uppercase tracking-[0.16em] text-primary">Demande metier</p>
            <h3 className="mt-2 text-2xl font-semibold">Lancer un nouveau travail</h3>
          </div>

          <div className="grid gap-4">
            <Textarea value={userInput} onChange={(event) => setUserInput(event.target.value)} />
            <div className="grid gap-4 md:grid-cols-2">
              <Input value={contextHint} onChange={(event) => setContextHint(event.target.value)} placeholder="Context hint optionnel" />
              <Select value={targetOutput} onChange={(event) => setTargetOutput(event.target.value)}>
                <option value="auto">auto</option>
                <option value="analysis">analysis</option>
                <option value="ticket">ticket</option>
                <option value="documentation">documentation</option>
              </Select>
            </div>
          </div>

          <Button
            onClick={() =>
              mutation.mutate({
                user_input: userInput,
                context_hint: contextHint || null,
                target_output: targetOutput,
              })
            }
          >
            Executer /process
          </Button>
        </CardContent>
      </Card>

      {mutation.data ? <ArtifactRenderer result={mutation.data.result} /> : null}
    </div>
  );
}
