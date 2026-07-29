const BASE = '/api/v1';

let _token: string | null = null;

export function setToken(t: string | null) { _token = t; }
export function getToken() { return _token; }

export async function api<T>(path: string, opts?: RequestInit): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (_token) headers['Authorization'] = `Bearer ${_token}`;
  const res = await fetch(`${BASE}${path}`, { ...opts, headers });
  if (res.status === 401) {
    window.dispatchEvent(new CustomEvent('cronos:unauthorized'));
    throw new Error('Unauthorized');
  }
  return res.json();
}

export async function login(username: string, password: string) {
  const res = await fetch(`${BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error('Login failed');
  const data = await res.json();
  _token = data.token;
  return data;
}

export async function getKpisPerformance(master?: string) {
  const q = master ? `?master=${master}` : '';
  return api<any>(`/kpis/performance${q}`);
}

export async function getJobs(master?: string, limit = 100, offset = 0) {
  const q = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (master) q.set('master', master);
  return api<any[]>(`/jobs?${q}`);
}

export async function getMasters() {
  return api<any[]>('/masters');
}

export async function getAssets(master?: string) {
  const q = master ? `?master=${master}` : '';
  return api<any[]>(`/assets${q}`);
}

export async function getKpisStorage(master?: string) {
  const q = master ? `?master=${master}` : '';
  return api<any[]>(`/kpis/storage${q}`);
}

export async function triggerCollect(masterId?: string) {
  const path = masterId ? `/collect/${masterId}` : '/collect';
  return api<any>(path, { method: 'POST' });
}
