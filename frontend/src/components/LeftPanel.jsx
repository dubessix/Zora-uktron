import React from 'react';
import useMetricHistory from '../hooks/useMetricHistory';
import { formatBytesPerSecond } from '../utils/metricHistory';

/** Dashboard summary using only values reported by /api/health. */
export default function LeftPanel({ systemMetrics }) {
  const metrics = systemMetrics || {};
  const { history, networkRates } = useMetricHistory(systemMetrics);
  const cpu = numberOrNull(metrics.cpu_percent);
  const ram = numberOrNull(metrics.ram_percent ?? metrics.total_system_ram_usage_percent);
  const temperature = numberOrNull(metrics.temperature_c);
  const disk = numberOrNull(metrics.disk_percent);
  const uptime = numberOrNull(metrics.uptime_seconds);
  const healthLatency = numberOrNull(metrics.health_latency_ms);
  const network = metrics.network || {};
  const hasTelemetry = cpu !== null && ram !== null;
  const hasTrendHistory = history.cpu.length >= 2 && history.ram.length >= 2;

  return (
    <aside className="col-span-12 lg:col-span-3 h-full flex flex-col gap-4 overflow-y-auto pr-1">
      <section className="bg-[#14141E]/80 border border-white/5 p-4 rounded-sm backdrop-blur-2xl">
        <div className="flex justify-between items-center mb-3">
          <span className="text-[9px] uppercase font-bold tracking-widest text-[#F5F5F7]">System overview</span>
          <span className={`text-[7px] tracking-widest font-mono uppercase ${hasTelemetry ? 'text-emerald-400' : 'text-amber-300'}`}>
            {hasTelemetry ? (hasTrendHistory ? 'Live trends' : 'Collecting trends') : 'Waiting for backend'}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-3 font-mono text-[10px]">
          <MetricCard label="CPU" value={percent(cpu)} color="text-emerald-400" progress={cpu} />
          <MetricCard label="RAM" value={percent(ram)} color="text-amber-400" progress={ram} />
          <MetricCard label="Temperature" value={temperature === null ? 'Unavailable' : `${temperature.toFixed(1)}°C`} color="text-rose-400" />
          <MetricCard label="Disk used" value={percent(disk)} color="text-purple-400" progress={disk} />
        </div>
      </section>

      <section className="bg-[#14141E]/80 border border-white/5 p-4 rounded-sm backdrop-blur-2xl font-mono">
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-[10px] uppercase font-bold tracking-widest text-[#F5F5F7]">Network counters</h2>
          <span className={`text-[7px] uppercase ${network.available ? 'text-sky-300' : 'text-amber-300'}`}>
            {network.available ? 'Reported' : 'Unavailable'}
          </span>
        </div>
        {network.available ? (
          <div className="space-y-2 text-[8px] text-white/50">
            <div className="flex justify-between"><span>Interfaces up</span><span>{network.interfaces_up}</span></div>
            <div className="flex justify-between"><span>Local round trip</span><span>{healthLatency === null ? 'Unavailable' : `${healthLatency.toFixed(1)} ms`}</span></div>
            <div className="flex justify-between"><span>TX rate</span><span>{networkRates.available ? formatBytesPerSecond(networkRates.txBytesPerSecond) : rateStatus(networkRates.status)}</span></div>
            <div className="flex justify-between"><span>RX rate</span><span>{networkRates.available ? formatBytesPerSecond(networkRates.rxBytesPerSecond) : rateStatus(networkRates.status)}</span></div>
          </div>
        ) : (
          <p className="text-[8px] text-white/30">This device did not report network counters.</p>
        )}
      </section>

      <section className="grid grid-cols-2 gap-3">
        <SmallMetric label="Backend process RAM" value={metrics.process_ram_mb == null ? 'Unavailable' : `${metrics.process_ram_mb} MB`} />
        <SmallMetric label="System uptime" value={uptime === null ? 'Unavailable' : `${(uptime / 3600).toFixed(1)} h`} />
        <SmallMetric label="Battery" value={metrics.battery_display || 'Unavailable'} />
        <SmallMetric label="Platform" value={metrics.platform || 'Unavailable'} />
      </section>
    </aside>
  );
}

function MetricCard({ label, value, color, progress }) {
  return (
    <div className="bg-white/[0.01] border border-white/5 p-2 rounded-sm">
      <span className="text-[7px] text-[#8B8B96] uppercase tracking-wider block">{label}</span>
      <span className={`text-sm font-bold mt-1 block break-words ${color}`}>{value}</span>
      {progress !== null && progress !== undefined && (
        <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden mt-2">
          <div className="h-full bg-current opacity-70" style={{ width: `${Math.max(0, Math.min(100, progress))}%` }} />
        </div>
      )}
    </div>
  );
}

function SmallMetric({ label, value }) {
  return (
    <div className="bg-[#14141E]/80 border border-white/5 p-3 rounded-sm backdrop-blur-2xl min-w-0">
      <span className="text-[7px] uppercase tracking-widest text-[#8B8B96] block">{label}</span>
      <span className="text-[9px] font-bold text-[#F5F5F7] mt-1.5 block font-mono break-words">{value}</span>
    </div>
  );
}

function numberOrNull(value) {
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
}

function percent(value) {
  return value === null ? 'Unavailable' : `${value.toFixed(1)}%`;
}

function rateStatus(status) {
  if (status === 'collecting') return 'Collecting…';
  if (status === 'counter_reset') return 'Counter reset';
  return 'Unavailable';
}
