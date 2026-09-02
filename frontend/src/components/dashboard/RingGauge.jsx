export const RingGauge = ({ value = 0, label, sublabel, testId, size = 128 }) => {
  const radius = (size - 16) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, value || 0));
  const offset = circumference - (clamped / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-3" data-testid={testId}>
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth={2}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#FFFFFF"
            strokeWidth={2}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-700 ease-out drop-shadow-[0_0_6px_rgba(255,255,255,0.6)]"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-extrabold font-mono tracking-tighter text-white">
            {Math.round(clamped)}%
          </span>
        </div>
      </div>
      <div className="text-center">
        <div className="text-xs font-mono tracking-[0.25em] uppercase text-neutral-400">{label}</div>
        {sublabel && <div className="text-[11px] font-mono text-neutral-500 mt-0.5">{sublabel}</div>}
      </div>
    </div>
  );
};
