import { useEffect, useState } from "react";
import { api } from "../../lib/api";

export const DesktopModal = ({ open, onClose }) => {
  const [info, setInfo] = useState(null);

  useEffect(() => {
    if (open) {
      api
        .get("/desktop/open")
        .then(({ data }) => setInfo(data))
        .catch(() => setInfo({ available: false }));
    }
  }, [open]);

  if (!open) return null;

  return (
    <div data-testid="desktop-modal-container" className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-6">
      <div className="relative w-full h-full max-w-6xl border border-white/20 bg-black flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-white/15">
          <span className="text-xs font-mono tracking-[0.25em] uppercase text-neutral-400">
            Remote Desktop Viewer
          </span>
          <button
            data-testid="btn-close-desktop-modal"
            onClick={onClose}
            className="px-3 py-1.5 border border-white/30 text-white font-mono text-xs uppercase hover:bg-white hover:text-black transition-all"
          >
            Close
          </button>
        </div>
        <div className="flex-1 flex items-center justify-center">
          {info?.available ? (
            <iframe title="desktop" src={info.url} className="w-full h-full border-0" />
          ) : (
            <p className="text-xs font-mono text-neutral-500 text-center max-w-md px-6 leading-relaxed">
              Remote desktop unavailable — the Docker daemon / desktop container isn't reachable from this
              environment. Deploy this stack on a real Docker host and set DESKTOP_URL in backend/.env to view
              the live Ubuntu desktop here.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
