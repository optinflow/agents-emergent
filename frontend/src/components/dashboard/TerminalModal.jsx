import { useEffect, useRef } from "react";
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";
import "xterm/css/xterm.css";
import { WS_BASE } from "../../lib/api";

export const TerminalModal = ({ open, onClose }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!open || !containerRef.current) return;

    const term = new Terminal({
      cursorBlink: true,
      theme: { background: "#000000", foreground: "#FFFFFF", cursor: "#FFFFFF" },
      fontFamily: "'JetBrains Mono', monospace",
      fontSize: 13,
    });
    const fit = new FitAddon();
    term.loadAddon(fit);
    term.open(containerRef.current);
    fit.fit();

    const ws = new WebSocket(`${WS_BASE}/api/desktop/terminal/ws`);
    ws.binaryType = "arraybuffer";
    ws.onmessage = (evt) => {
      if (typeof evt.data === "string") term.write(evt.data);
      else term.write(new Uint8Array(evt.data));
    };
    ws.onclose = () => term.write("\r\n[connection closed]\r\n");
    term.onData((data) => {
      if (ws.readyState === WebSocket.OPEN) ws.send(data);
    });

    const handleResize = () => fit.fit();
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      ws.close();
      term.dispose();
    };
  }, [open]);

  if (!open) return null;

  return (
    <div data-testid="terminal-modal-container" className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-6">
      <div className="relative w-full h-full max-w-5xl border border-white/20 bg-black flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-white/15">
          <span className="text-xs font-mono tracking-[0.25em] uppercase text-neutral-400">
            CLI Terminal Console
          </span>
          <button
            data-testid="btn-close-terminal-modal"
            onClick={onClose}
            className="px-3 py-1.5 border border-white/30 text-white font-mono text-xs uppercase hover:bg-white hover:text-black transition-all"
          >
            Close
          </button>
        </div>
        <div data-testid="terminal-input-field" ref={containerRef} className="flex-1 p-3 overflow-hidden" />
      </div>
    </div>
  );
};
