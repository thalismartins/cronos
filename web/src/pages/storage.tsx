import { useEffect, useState } from 'preact/hooks';
import type { JSX } from 'preact';
import { getKpisStorage } from '../api';

export function StoragePage(): JSX.Element {
  const [storage, setStorage] = useState<any[]>([]);

  useEffect(() => { getKpisStorage().then(setStorage); }, []);

  return (
    <div class="page">
      <h1 class="page-title">Storage</h1>
      <div class="kpi-grid">
        {storage.map(s => (
          <div class="kpi-card" key={s.master_id}>
            <div class="kpi-label">{s.master_id}</div>
            <div class="kpi-value">{(s.used_capacity / 1024).toFixed(1)} TB</div>
            <div class="progress-bar"><div class="progress-fill" style={{ width: `${Math.min(100, (s.used_capacity / s.total_capacity) * 100)}%` }} /></div>
            <div class="kpi-label">{(s.total_capacity / 1024).toFixed(1)} TB total · {s.pool_count} pools</div>
            <div class="kpi-label">Avg dedup: {s.avg_dedup?.toFixed(2)}x</div>
          </div>
        ))}
      </div>
    </div>
  );
}
