import { useEffect, useState } from "react";

export const Header = ({ dockerAvailable }) => {
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <header
      data-testid="app-header"
      className="col-span-full flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/15 pb-6 mb-2"
    >
      <div>
        <div className="text-xs font-mono tracking-[0.25em] uppercase text-neutral-400 mb-1">
          Personal AI Computer
        </div>
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tighter uppercase font-mono text-white">
          Control Panel
        </h1>
      </div>
      <div className="flex items-center gap-4">
        <div className="text-xs font-mono text-neutral-400">{now.toLocaleString()}</div>
        <div
          data-testid="docker-daemon-status"
          className={`px-3 py-1.5 border text-xs font-mono uppercase tracking-widest ${
            dockerAvailable ? "border-white text-white" : "border-white/30 text-neutral-500"
          }`}
        >
          Docker {dockerAvailable ? "Online" : "Unavailable"}
        </div>
      </div>
    </header>
  );
};
