import { useEffect, useState } from "react";
import { Panel } from "./Panel";
import { api } from "../../lib/api";
import { toast } from "sonner";

const fmtBytes = (n) => {
  if (!n) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let i = 0;
  let val = n;
  while (val >= 1024 && i < units.length - 1) {
    val /= 1024;
    i++;
  }
  return `${val.toFixed(1)} ${units[i]}`;
};

export const BackupPanel = () => {
  const [backups, setBackups] = useState([]);
  const [creating, setCreating] = useState(false);
  const [restoring, setRestoring] = useState(null);
  const [confirmTarget, setConfirmTarget] = useState(null);

  const refresh = async () => {
    try {
      const { data } = await api.get("/backups");
      setBackups(data);
    } catch (e) {
      // ignore
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const createBackup = async () => {
    setCreating(true);
    try {
      await api.post("/backups", {});
      toast.success("Snapshot created");
      refresh();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Backup failed");
    } finally {
      setCreating(false);
    }
  };

  const restore = async (filename) => {
    setRestoring(filename);
    try {
      await api.post(`/backups/${filename}/restore`);
      toast.success("Restore complete");
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Restore failed");
    } finally {
      setRestoring(null);
      setConfirmTarget(null);
    }
  };

  return (
    <Panel title="Snapshot & Backup Manager" testId="backup-panel">
      <button
        data-testid="btn-create-snapshot"
        disabled={creating}
        onClick={createBackup}
        className="px-5 py-2.5 bg-white text-black font-mono font-bold text-xs uppercase tracking-widest border border-white hover:bg-neutral-200 transition-all disabled:opacity-40 mb-5"
      >
        {creating ? "Creating..." : "Create Snapshot"}
      </button>
      <div data-testid="snapshot-list" className="space-y-3 max-h-72 overflow-auto">
        {backups.length === 0 && <div className="text-xs font-mono text-neutral-500">No snapshots yet.</div>}
        {backups.map((b, idx) => (
          <div key={b.filename} className="flex items-center justify-between border-b border-white/10 pb-2 gap-3">
            <div>
              <div className="text-xs font-mono text-white">{b.filename}</div>
              <div className="text-[11px] font-mono text-neutral-500">
                {fmtBytes(b.size_bytes)} · {new Date(b.created_at).toLocaleString()}
              </div>
            </div>
            {confirmTarget === b.filename ? (
              <div className="flex gap-2">
                <button
                  data-testid={`btn-confirm-restore-${idx}`}
                  onClick={() => restore(b.filename)}
                  disabled={restoring !== null}
                  className="px-3 py-1.5 bg-white text-black font-mono text-[11px] uppercase tracking-widest border border-white"
                >
                  Confirm
                </button>
                <button
                  data-testid={`btn-cancel-restore-${idx}`}
                  onClick={() => setConfirmTarget(null)}
                  className="px-3 py-1.5 bg-transparent text-white font-mono text-[11px] uppercase tracking-widest border border-white/30"
                >
                  Cancel
                </button>
              </div>
            ) : (
              <button
                data-testid={`btn-restore-snapshot-${idx}`}
                onClick={() => setConfirmTarget(b.filename)}
                className="px-3 py-1.5 bg-transparent text-white font-mono text-[11px] uppercase tracking-widest border border-white/30 hover:border-white hover:bg-white/10 transition-all"
              >
                Restore
              </button>
            )}
          </div>
        ))}
      </div>
    </Panel>
  );
};
