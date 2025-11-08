import type { ModelCard } from "../types/api";

interface Props {
  models: ModelCard[];
  selectedModelId?: string;
  onSelect: (modelId: string) => void;
}

export function ModelList({ models, selectedModelId, onSelect }: Props) {
  if (!models.length) {
    return <p className="text-sm text-slate-400">No models registered yet.</p>;
  }

  return (
    <ul className="space-y-3">
      {models.map((model) => (
        <li key={model.id}>
          <button
            type="button"
            className={`w-full text-left border rounded-xl px-4 py-3 transition hover:border-brand-400 ${
              selectedModelId === model.id ? "border-brand-500 bg-brand-500/10" : "border-slate-700 bg-slate-800/50"
            }`}
            onClick={() => onSelect(model.id)}
          >
            <p className="font-semibold text-slate-100">{model.name}</p>
            <p className="text-xs text-slate-400">{model.description}</p>
            <p className="text-xs text-slate-500 mt-1">
              {model.quantization} • {model.context_length} ctx • {model.parameter_count}B params
            </p>
          </button>
        </li>
      ))}
    </ul>
  );
}
