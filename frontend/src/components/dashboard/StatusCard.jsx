import { useState } from "react";
import { Panel } from "./Panel";
import { api } from "../../lib/api";
import { toast } from "sonner";

export const StatusCard = ({ status, onRefresh, onOpenDesktop, onOpenTerminal }) => {
  const [loadingAction, setLoadingAction] = useState(null);
  const desktop = status?.desktop || {};
  const dockerAvailable = status?.docker_available;

  const runAction = async (action, endpoint) => {
    setLoadingAction(action);
    try {
      await api.post(endpoint);
      toast.success(`Desktop ${action} sent`);
      onRefresh();
    } catch (e) {
      toast.error(e?.response?.data?.detail || `Failed to ${action}`);
    } finally {
      setLoadingAction(null);
    }
  };

  const statusLabel = !dockerAvailable ? "UNAVAILABLE" : (desktop.status || "unknown").toUpperCase();

  return (
    <Panel title="Desktop Container" testId="container-status-panel">
      <div className="flex flex-wrap items-center gap-3 mb-6">
        <span
          data-testid="system-status-badge"
          className={`px-4 py-2 border font-mono text-xs uppercase tracking-widest ${
            desktop.status === "running" ? "border-white text-white" : "border-white/30 text-neutral-500"
          }`}
        >
          {statusLabel}
        </span>
        <span className="text-xs font-mono text-neutral-500">{status?.container_name}</span>
      </div>
      <div className="flex flex-wrap gap-3 mb-6">
        <button
          data-testid="btn-start-container"
          disabled={loadingAction !== null}
          onClick={() => runAction("start", "/desktop/start")}
          className="px-5 py-2.5 bg-white text-black font-mono font-bold text-xs uppercase tracking-widest border border-white hover:bg-neutral-200 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-40"
        >
          Start
        </button>
        <button
          data-testid="btn-stop-container"
          disabled={loadingAction !== null}
          onClick={() => runAction("stop", "/desktop/stop")}
          className="px-5 py-2.5 bg-transparent text-white font-mono font-medium text-xs uppercase tracking-widest border border-white/30 hover:border-white hover:bg-white/10 active:scale-[0.98] transition-all disabled:opacity-40"
        >
          Stop
        </button>
        <button
          data-testid="btn-restart-container"
          disabled={loadingAction !== null}
          onClick={() => runAction("restart", "/desktop/restart")}
          className="px-5 py-2.5 bg-neutral-950 text-white font-mono font-bold text-xs uppercase tracking-widest border border-white/60 hover:bg-white hover:text-black transition-all disabled:opacity-40"
        >
          Restart
        </button>
      </div>
      <div className="flex flex-wrap gap-3">
        <button
          data-testid="btn-open-desktop"
          onClick={onOpenDesktop}
          className="px-5 py-2.5 bg-white text-black font-mono font-bold text-xs uppercase tracking-widest border border-white hover:bg-neutral-200 transition-all"
        >
          Open Desktop
        </button>
        <button
          data-testid="btn-open-terminal"
          onClick={onOpenTerminal}
          className="px-5 py-2.5 bg-transparent text-white font-mono font-medium text-xs uppercase tracking-widest border border-white/30 hover:border-white hover:bg-white/10 transition-all"
        >
          Open Terminal
        </button>
      </div>
      {!dockerAvailable && (
        <p data-testid="docker-unavailable-note" className="mt-5 text-xs font-mono text-neutral-500 leading-relaxed">
          Docker daemon not detected in this environment. Deploy this stack (see README) on a Docker host to
          control a real desktop container.
        </p>
      )}
    </Panel>
  );
};
