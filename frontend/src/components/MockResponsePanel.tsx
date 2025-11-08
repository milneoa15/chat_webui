import type { ChatResponse } from "../types/api";

interface Props {
  response?: ChatResponse;
  isLoading: boolean;
}

export function MockResponsePanel({ response, isLoading }: Props) {
  if (isLoading) {
    return <p className="text-sm text-slate-400">Streaming mock tokens…</p>;
  }

  if (!response) {
    return <p className="text-sm text-slate-500">Trigger a prompt to preview the mocked stream.</p>;
  }

  return (
    <div className="space-y-2">
      {response.stream.map((chunk) => (
        <p key={chunk.index} className={`text-slate-100 ${chunk.is_final ? "font-semibold" : ""}`}>
          {chunk.token}
        </p>
      ))}
    </div>
  );
}
