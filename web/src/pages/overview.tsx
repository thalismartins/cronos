import { useEffect, useState } from 'preact/hooks';
import type { JSX } from 'preact';
import { getKpisPerformance, getKpisStorage, getMasters, api } from '../api';

interface Kpis { total_jobs: number; success_jobs: number; fail_jobs: number; success_rate: number }
interface Master { id: string; alias: string; freshness_status: string; last_collected_at: string }
interface StorageItem { master_id: string; pool_count: number; total_capacity: number; used_capacity: number; avg_dedup: number }

export function OverviewPage(): JSX.Element {
  const [kpis, setKpis] = useState<Kpis | null>(null);
  const [storage, setStorage] = useState<StorageItem[]>([]);
  const [masters, setMasters] = useState<Master[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getKpisPerformance(),
      getKpisStorage(),
      getMasters(),
    ]).then(([k, s, m]) => {
      setKpis(k);
      setStorage(s);
      setMasters(m);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <div class="page"><div class="skelbar" style="height:200px" /></div>;

  return (
    <div class="page">
      <h1 class="page-title">Overview</h1>
      <div class="kpi-grid">
        <div class="kpi-card"><div class="kpi-value">{kpis?.total_jobs ?? 0}</div><div class="kpi-label">Total Jobs</div></div>
        <div class="kpi-card ok"><div class="kpi-value">{kpis?.success_jobs ?? 0}</div><div class="kpi-label">Success</div></div>
        <div class="kpi-card err"><div class="kpi-value">{kpis?.fail_jobs ?? 0}</div><div class="kpi-label">Failed</div></div>
        <div class="kpi-card accent"><div class="kpi-value">{kpis?.success_rate ?? 0}%</div><div class="kpi-label">Success Rate</div></div>
      </div>
      <h2 class="section-title">Masters</h2>
      <table class="data-table">
        <thead><tr><th>Alias</th><th>Status</th><th>Last Collected</th></tr></thead>
        <tbody>
          {masters.map(m => (
            <tr key={m.id}>
              <td>{m.alias}</td>
              <td><span class={`badge badge-${m.freshness_status === 'ok' ? 'success' : m.freshness_status === 'violated' ? 'error' : 'muted'}`}>{m.freshness_status}</span></td>
              <td>{m.last_collected_at ? new Date(m.last_collected_at).toLocaleString() : 'never'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <h2 class="section-title">Storage</h2>
      <div class="kpi-grid">
        {storage.map(s => (
          <div class="kpi-card" key={s.master_id}>
            <div class="kpi-label">{s.master_id}</div>
            <div class="kpi-value">{(s.used_capacity / 1024).toFixed(1)} TB</div>
            <div class="kpi-label">/ {(s.total_capacity / 1024).toFixed(1)} TB · {s.avg_dedup.toFixed(1)}x dedup</div>
          </div>
        ))}
      </div>
    </div>
  );
}
