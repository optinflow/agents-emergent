import { useEffect, useState } from "react";
import { Panel } from "./Panel";
import { RingGauge } from "./RingGauge";
import { api } from "../../lib/api";

const fmtBytes = (n) => {
  if (!n) return "0 GB";
  return `${(n / 1024 / 1024 / 1024).toFixed(1)} GB`;
};

export const TelemetryPanel = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await api.get("/system/stats");
        setStats(data);
      } catch (e) {
        // ignore transient polling errors
      }
    };
    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, []);

  const source = stats?.desktop_stats ? "desktop" : "host";
  const cpu = stats?.desktop_stats?.cpu_percent ?? stats?.host_stats?.cpu_percent ?? 0;
  const ram = stats?.desktop_stats?.mem_percent ?? stats?.host_stats?.mem_percent ?? 0;
  const disk = stats?.host_stats?.disk_percent ?? 0;

  return (
    <Panel title="System Telemetry" testId="telemetry-panel">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <RingGauge
          testId="gauge-cpu"
          value={cpu}
          label="CPU"
          sublabel={source === "desktop" ? "Desktop Container" : "Dashboard Host"}
        />
        <RingGauge
          testId="gauge-ram"
          value={ram}
          label="RAM"
          sublabel={stats?.host_stats ? fmtBytes(stats.host_stats.mem_used) : "--"}
        />
        <RingGauge
          testId="gauge-disk"
          value={disk}
          label="Disk"
          sublabel={stats?.host_stats ? fmtBytes(stats.host_stats.disk_used) : "--"}
        />
      </div>
      {!stats?.docker_available && (
        <p className="mt-5 text-xs font-mono text-neutral-500">
          Desktop container telemetry unavailable — showing dashboard host metrics instead.
        </p>
      )}
    </Panel>
  );
};
