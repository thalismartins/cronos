import { useEffect, useState } from 'preact/hooks';
import type { JSX } from 'preact';
import { api, triggerCollect } from '../api';

export function CollectorsPage(): JSX.Element {
  const [collectors, setCollectors] = useState<any[]>([]);
  const [runs, setRuns] = useState<any[]>([]);

  const load = () => {
    api<any[]>('/masters').then(setCollectors);
    api<any[]>('/collection-runs').then(setRuns).catch(() => {});
  };

  useEffect(load, []);

  const handleCollect = async (masterId?: string) => {
    await triggerCollect(masterId);
    setTimeout(load, 1000);
  };

  return (
    <div class="page">
      <h1 class="page-title">Collectors</h1>
      <button class="btn btn-primary" onClick={() => handleCollect()}>Collect All</button>
      <table class="data-table" style="margin-top:16px">
        <thead><tr><th>Collector</th><th>Master</th><th>Freshness</th><th>Actions</th></tr></thead>
        <tbody>
          {collectors.map(m => (
            <tr key={m.id}>
              <td>{m.collector_id}</td>
              <td><strong>{m.alias}</strong></td>
              <td><span class={`badge badge-${m.freshness_status === 'ok' ? 'success' : m.freshness_status === 'violated' ? 'error' : 'muted'}`}>{m.freshness_status}</span></td>
              <td><button class="btn btn-sm" onClick={() => handleCollect(m.id)}>Collect</button></td>
            </tr>
          ))}
        </tbody>
      </table>
      <h2 class="section-title">Recent Runs</h2>
      <table class="data-table">
        <thead><tr><th>ID</th><th>Collector</th><th>Master</th><th>Status</th><th>Records</th><th>Started</th></tr></thead>
        <tbody>
          {runs.slice(0, 20).map(r => (
            <tr key={r.id}>
              <td class="cell-mono">#{r.id}</td>
              <td>{r.collector_id}</td>
              <td>{r.master_id}</td>
              <td><span class={`badge badge-${r.status === 'success' ? 'success' : r.status === 'failed' ? 'error' : 'warn'}`}>{r.status}</span></td>
              <td>{r.records_collected || 0}</td>
              <td>{r.start_time ? new Date(r.start_time).toLocaleString() : '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
