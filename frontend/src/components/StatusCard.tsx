interface StatusCardProps {
  title: string;
  value: string;
  subtitle?: string;
  tone?: "success" | "warning" | "error";
}

const tones: Record<NonNullable<StatusCardProps["tone"]>, string> = {
  success: "text-emerald-300 bg-emerald-900/30 border-emerald-500/30",
  warning: "text-amber-300 bg-amber-900/30 border-amber-500/30",
  error: "text-rose-300 bg-rose-900/30 border-rose-500/30",
};

export function StatusCard({ title, value, subtitle, tone = "success" }: StatusCardProps) {
  return (
    <div className={`border rounded-xl px-4 py-3 ${tones[tone]} shadow-lg`}>
      <p className="text-xs uppercase tracking-widest text-slate-300">{title}</p>
      <p className="text-2xl font-semibold">{value}</p>
      {subtitle ? <p className="text-xs text-slate-400">{subtitle}</p> : null}
    </div>
  );
}
