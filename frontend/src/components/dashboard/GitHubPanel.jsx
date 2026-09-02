import { useEffect, useState } from "react";
import { Panel } from "./Panel";
import { api } from "../../lib/api";
import { toast } from "sonner";

export const GitHubPanel = () => {
  const [status, setStatus] = useState(null);
  const [commits, setCommits] = useState([]);
  const [busy, setBusy] = useState(null);
  const [log, setLog] = useState("");

  const refresh = async () => {
    try {
      const [s, c] = await Promise.all([api.get("/github/status"), api.get("/github/commits")]);
      setStatus(s.data);
      setCommits(c.data.commits || []);
    } catch (e) {
      toast.error("Failed to load repo status");
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const run = async (action) => {
    setBusy(action);
    setLog(`${action}...`);
    try {
      const { data } = await api.post(`/github/${action}`);
      setLog(JSON.stringify(data.output || data, null, 2));
      toast.success(`${action} complete`);
      refresh();
    } catch (e) {
      const detail = e?.response?.data?.detail || `${action} failed`;
      setLog(detail);
      toast.error(detail);
    } finally {
      setBusy(null);
    }
  };

  return (
    <Panel title="GitHub Sync" testId="github-panel">
      <div className="space-y-2 mb-5 text-sm font-mono text-neutral-300">
        <div>
          Branch: <span className="text-white">{status?.branch || "--"}</span>
        </div>
        <div>
          Remote: <span className="text-white">{status?.remote_url || "not configured"}</span>
        </div>
        <div>
          Working Tree:{" "}
          <span className="text-white">
            {status?.clean ? "Clean" : `${status?.changes?.length || 0} change(s)`}
          </span>
        </div>
        {!status?.configured && (
          <div className="text-neutral-500 text-xs">
            Set GITHUB_TOKEN and GITHUB_REPO_URL in backend/.env to enable Push/Pull/Sync.
          </div>
        )}
      </div>
      <div className="flex flex-wrap gap-3 mb-5">
        <button
          data-testid="btn-github-push"
          disabled={busy !== null}
          onClick={() => run("push")}
          className="px-5 py-2.5 bg-white text-black font-mono font-bold text-xs uppercase tracking-widest border border-white hover:bg-neutral-200 transition-all disabled:opacity-40"
        >
          Push
        </button>
        <button
          data-testid="btn-github-pull"
          disabled={busy !== null}
          onClick={() => run("pull")}
          className="px-5 py-2.5 bg-transparent text-white font-mono font-medium text-xs uppercase tracking-widest border border-white/30 hover:border-white hover:bg-white/10 transition-all disabled:opacity-40"
        >
          Pull
        </button>
        <button
          data-testid="btn-github-sync"
          disabled={busy !== null}
          onClick={() => run("sync")}
          className="px-5 py-2.5 bg-neutral-950 text-white font-mono font-bold text-xs uppercase tracking-widest border border-white/60 hover:bg-white hover:text-black transition-all disabled:opacity-40"
        >
          Sync
        </button>
      </div>
      {log && (
        <pre
          data-testid="github-log-output"
          className="text-xs font-mono text-neutral-400 border border-white/10 p-3 mb-5 max-h-24 overflow-auto"
        >
          {log}
        </pre>
      )}
      <div data-testid="commits-list" className="space-y-3 max-h-56 overflow-auto">
        {commits.length === 0 && <div className="text-xs font-mono text-neutral-500">No commits found.</div>}
        {commits.map((c) => (
          <div key={c.sha} className="border-b border-white/10 pb-2">
            <div className="text-xs font-mono text-white">
              {c.sha.slice(0, 7)} — {c.message}
            </div>
            <div className="text-[11px] font-mono text-neutral-500">
              {c.author} · {new Date(c.date).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
    </Panel>
  );
};
