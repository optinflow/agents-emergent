import { useEffect, useState } from "react";
import { Header } from "../components/dashboard/Header";
import { StatusCard } from "../components/dashboard/StatusCard";
import { TelemetryPanel } from "../components/dashboard/TelemetryPanel";
import { GitHubPanel } from "../components/dashboard/GitHubPanel";
import { BackupPanel } from "../components/dashboard/BackupPanel";
import { DesktopModal } from "../components/dashboard/DesktopModal";
import { TerminalModal } from "../components/dashboard/TerminalModal";
import { api } from "../lib/api";

export default function Dashboard() {
  const [status, setStatus] = useState(null);
  const [desktopOpen, setDesktopOpen] = useState(false);
  const [terminalOpen, setTerminalOpen] = useState(false);

  const refreshStatus = async () => {
    try {
      const { data } = await api.get("/system/status");
      setStatus(data);
    } catch (e) {
      // ignore transient polling errors
    }
  };

  useEffect(() => {
    refreshStatus();
    const t = setInterval(refreshStatus, 8000);
    return () => clearInterval(t);
  }, []);

  return (
    <div data-testid="dashboard-root" className="min-h-screen bg-[#050505] text-white">
      <div className="max-w-[1600px] mx-auto grid grid-cols-1 md:grid-cols-12 gap-4 md:gap-6 p-4 sm:p-6 md:p-8">
        <Header dockerAvailable={status?.docker_available} />
        <div className="col-span-full md:col-span-8 lg:col-span-7">
          <StatusCard
            status={status}
            onRefresh={refreshStatus}
            onOpenDesktop={() => setDesktopOpen(true)}
            onOpenTerminal={() => setTerminalOpen(true)}
          />
        </div>
        <div className="col-span-full md:col-span-4 lg:col-span-5">
          <TelemetryPanel />
        </div>
        <div className="col-span-full md:col-span-6">
          <GitHubPanel />
        </div>
        <div className="col-span-full md:col-span-6">
          <BackupPanel />
        </div>
      </div>
      <DesktopModal open={desktopOpen} onClose={() => setDesktopOpen(false)} />
      <TerminalModal open={terminalOpen} onClose={() => setTerminalOpen(false)} />
    </div>
  );
}
