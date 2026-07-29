import { useEffect, useState } from 'preact/hooks';
import type { JSX } from 'preact';
import { getJobs } from '../api';

interface Job { id: number; master_id: string; ext_id: string; job_type: string; state: string; status_code: number; start_time: string; duration_seconds: number }

export function JobsPage(): JSX.Element {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getJobs().then(setJobs).finally(() => setLoading(false));
  }, []);

  return (
    <div class="page">
      <h1 class="page-title">Jobs</h1>
      {loading ? <div class="skelbar" style="height:400px" /> : (
        <table class="data-table">
          <thead><tr><th>ID</th><th>Master</th><th>Type</th><th>State</th><th>Code</th><th>Start</th><th>Duration</th></tr></thead>
          <tbody>
            {jobs.map(j => (
              <tr key={j.id}>
                <td class="cell-mono">{j.ext_id?.slice(0, 16)}</td>
                <td>{j.master_id}</td>
                <td>{j.job_type || '—'}</td>
                <td><span class={`badge badge-${j.status_code === 0 ? 'success' : j.status_code === 1 ? 'warn' : 'error'}`}>{j.state || '—'}</span></td>
                <td class="cell-mono">{j.status_code}</td>
                <td>{j.start_time ? new Date(j.start_time).toLocaleString() : '—'}</td>
                <td>{j.duration_seconds ? `${Math.round(j.duration_seconds / 60)}m` : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
