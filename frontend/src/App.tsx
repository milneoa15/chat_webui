import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { createMockChat, fetchHealth, fetchModels } from "./lib/api";
import type { ChatRequest } from "./types/api";
import { useChatConfig } from "./store/chatConfig";
import { StatusCard } from "./components/StatusCard";
import { ModelList } from "./components/ModelList";
import { ConfigForm } from "./components/ConfigForm";
import { MockResponsePanel } from "./components/MockResponsePanel";

function App() {
  const { config } = useChatConfig();
  const [selectedModel, setSelectedModel] = useState<string>();
  const [prompt, setPrompt] = useState("Explain how this mock backend will evolve once llama.cpp is wired in.");
  const [systemPrompt, setSystemPrompt] = useState("You are a helpful local assistant.");

  const health = useQuery({ queryKey: ["health"], queryFn: fetchHealth });
  const models = useQuery({ queryKey: ["models"], queryFn: fetchModels });

  const fallbackModelId = useMemo(() => models.data?.[0]?.id, [models.data]);
  const activeModelId = selectedModel ?? fallbackModelId;

  const chatMutation = useMutation({
    mutationFn: (payload: ChatRequest) => createMockChat(payload),
  });

  const handleSend = () => {
    if (!activeModelId || !prompt.trim()) {
      return;
    }

    chatMutation.mutate({
      model_id: activeModelId,
      prompt,
      system_prompt: systemPrompt,
      config,
    });
  };

  const statusTone = health.isSuccess ? "success" : health.isPending ? "warning" : "error";

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <header className="border-b border-slate-800 bg-slate-900/70 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div>
            <p className="text-sm font-semibold tracking-wide text-brand-300">Chatbot WebUI</p>
            <p className="text-xs text-slate-400">Phase 1 — frontend + backend scaffolding</p>
          </div>
          <div className="flex gap-4">
            <StatusCard
              title="Backend"
              value={health.isSuccess ? health.data.status : "pending"}
              subtitle={health.data?.version ?? "Checking..."}
              tone={statusTone}
            />
            <StatusCard
              title="Models"
              value={models.data?.length ? `${models.data.length}` : "0"}
              subtitle="Mock registry"
              tone={models.isSuccess ? "success" : "warning"}
            />
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-6xl gap-6 px-6 py-8 lg:grid-cols-3">
        <section className="space-y-6 lg:col-span-1">
          <div>
            <h2 className="text-sm uppercase tracking-wide text-slate-400 mb-2">Models</h2>
            {models.isPending ? (
              <p className="text-sm text-slate-400">Loading mock models…</p>
            ) : models.isError ? (
              <p className="text-sm text-rose-300">Failed to load models.</p>
            ) : (
              <ModelList models={models.data ?? []} selectedModelId={activeModelId} onSelect={setSelectedModel} />
            )}
          </div>
          <div>
            <div className="mb-2 flex items-center justify-between">
              <h2 className="text-sm uppercase tracking-wide text-slate-400">Inference config</h2>
              <button
                type="button"
                className="text-xs text-brand-300 hover:text-brand-200"
                onClick={() => window.location.reload()}
              >
                Reset
              </button>
            </div>
            <ConfigForm />
          </div>
        </section>

        <section className="space-y-4 rounded-2xl border border-slate-800 bg-slate-900/40 p-6 lg:col-span-2">
          <div>
            <label className="block text-xs uppercase tracking-wide text-slate-400">System prompt</label>
            <textarea
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900/60 p-3 text-sm focus:border-brand-400 focus:outline-none"
              value={systemPrompt}
              rows={3}
              onChange={(event) => setSystemPrompt(event.target.value)}
            />
          </div>
          <div>
            <label className="block text-xs uppercase tracking-wide text-slate-400">User prompt</label>
            <textarea
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-900/60 p-3 text-base focus:border-brand-400 focus:outline-none"
              value={prompt}
              rows={5}
              onChange={(event) => setPrompt(event.target.value)}
            />
          </div>
          <div className="flex justify-end">
            <button
              type="button"
              className="rounded-xl bg-brand-500 px-4 py-2 font-semibold text-white transition hover:bg-brand-400 disabled:opacity-50"
              disabled={!activeModelId || chatMutation.isPending}
              onClick={handleSend}
            >
              {chatMutation.isPending ? "Streaming…" : "Stream mock response"}
            </button>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-950/50 p-4">
            <h3 className="text-sm font-semibold text-slate-200 mb-2">Mock stream</h3>
            <MockResponsePanel response={chatMutation.data} isLoading={chatMutation.isPending} />
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
