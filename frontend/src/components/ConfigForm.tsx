import { useChatConfig } from "../store/chatConfig";

export function ConfigForm() {
  const { config, update } = useChatConfig();

  return (
    <div className="grid grid-cols-2 gap-4">
      {Object.entries(config).map(([key, value]) => (
        <label key={key} className="text-xs uppercase tracking-wide text-slate-300">
          {key.replace("_", " ")}
          <input
            className="mt-1 w-full rounded-md bg-slate-900/40 border border-slate-700 px-2 py-1 text-slate-50 focus:border-brand-400 focus:outline-none text-sm"
            type="number"
            step="any"
            value={value}
            onChange={(event) =>
              update({
                [key]: Number(event.target.value),
              } as Partial<typeof config>)
            }
          />
        </label>
      ))}
    </div>
  );
}
