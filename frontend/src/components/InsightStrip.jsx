export function InsightStrip({ label, value, accent = "text-[var(--gold)]" }) {
  return (
    <div className="glass-panel rounded-[24px] p-4">
      <p className="text-xs uppercase tracking-[0.24em] text-[var(--fog)]">{label}</p>
      <p className={`mt-3 text-2xl ${accent}`}>{value}</p>
    </div>
  );
}
