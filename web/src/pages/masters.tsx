import { useEffect, useState } from 'preact/hooks';
import type { JSX } from 'preact';
import { getMasters } from '../api';

export function MastersPage(): JSX.Element {
  const [masters, setMasters] = useState<any[]>([]);

  useEffect(() => { getMasters().then(setMasters); }, []);

  return (
    <div class="page">
      <h1 class="page-title">Masters</h1>
      <table class="data-table">
        <thead><tr><th>Alias</th><th>Collector</th><th>Family</th><th>Freshness SLA</th><th>Last Collected</th><th>Status</th></tr></thead>
        <tbody>
          {masters.map(m => (
            <tr key={m.id}>
              <td><strong>{m.alias}</strong></td>
              <td>{m.collector_id}</td>
              <td>{m.family || '—'}</td>
              <td>{m.sla_hours || 8}h</td>
              <td>{m.last_collected_at ? new Date(m.last_collected_at).toLocaleString() : 'never'}</td>
              <td><span class={`badge badge-${m.freshness_status === 'ok' ? 'success' : m.freshness_status === 'violated' ? 'error' : 'muted'}`}>{m.freshness_status}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
