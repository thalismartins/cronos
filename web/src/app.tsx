import { useEffect, useState } from 'preact/hooks';
import type { JSX } from 'preact';

type Theme = 'dark' | 'light';
type Page = 'overview' | 'jobs' | 'masters' | 'storage' | 'collectors' | 'login';

interface Session { user: string; role: string; token: string }

export function App(): JSX.Element {
  const [theme, setTheme] = useState<Theme>(
    (document.documentElement.getAttribute('data-theme') as Theme) || 'dark',
  );
  const [session, setSession] = useState<Session | null>(() => {
    try {
      const s = localStorage.getItem('cronos-session');
      return s ? JSON.parse(s) : null;
    } catch { return null; }
  });
  const [page, setPage] = useState<Page>('overview');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    try { localStorage.setItem('cronos-theme', theme); } catch {}
  }, [theme]);

  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark');

  useEffect(() => {
    const handler = () => { setSession(null); localStorage.removeItem('cronos-session'); };
    window.addEventListener('cronos:unauthorized', handler);
    return () => window.removeEventListener('cronos:unauthorized', handler);
  }, []);

  if (!session) {
    return <LoginPage onAuth={(s) => { setSession(s); setPage('overview'); }} />;
  }

  return (
    <div class="app-shell">
      <Sidebar page={page} onNavigate={setPage} theme={theme} onToggleTheme={toggleTheme} session={session} />
      <main class="main-content">
        {page === 'overview' && <OverviewPage />}
        {page === 'jobs' && <JobsPage />}
        {page === 'masters' && <MastersPage />}
        {page === 'storage' && <StoragePage />}
        {page === 'collectors' && <CollectorsPage />}
      </main>
    </div>
  );
}

function Sidebar({ page, onNavigate, theme, onToggleTheme, session }: {
  page: Page; onNavigate: (p: Page) => void; theme: Theme;
  onToggleTheme: () => void; session: Session;
}): JSX.Element {
  const items: { id: Page; icon: string; label: string }[] = [
    { id: 'overview', icon: '◉', label: 'Overview' },
    { id: 'jobs', icon: '≡', label: 'Jobs' },
    { id: 'masters', icon: '⬡', label: 'Masters' },
    { id: 'storage', icon: '▣', label: 'Storage' },
    { id: 'collectors', icon: '▶', label: 'Collectors' },
  ];

  return (
    <nav class="sidebar">
      <div class="sidebar-brand">Cronos</div>
      <div class="sidebar-nav">
        {items.map(item => (
          <button
            key={item.id}
            class={`sidebar-link ${page === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
          >
            <span class="sidebar-icon">{item.icon}</span>
            {item.label}
          </button>
        ))}
      </div>
      <div class="sidebar-footer">
        <button class="sidebar-link" onClick={onToggleTheme}>
          {theme === 'dark' ? '☀' : '☾'} {theme === 'dark' ? 'Light' : 'Dark'}
        </button>
        <div class="sidebar-user">{session.user} ({session.role})</div>
      </div>
    </nav>
  );
}

function LoginPage({ onAuth }: { onAuth: (s: Session) => void }): JSX.Element {
  const [user, setUser] = useState('');
  const [pass, setPass] = useState('');
  const [err, setErr] = useState('');

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    setErr('');
    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: user, password: pass }),
      });
      if (!res.ok) { setErr('Invalid credentials'); return; }
      const data = await res.json();
      const session: Session = { user: data.user, role: data.role, token: data.token };
      localStorage.setItem('cronos-session', JSON.stringify(session));
      onAuth(session);
    } catch { setErr('Connection error'); }
  };

  return (
    <div class="login-page">
      <form class="login-card" onSubmit={handleSubmit}>
        <h1 class="login-title">Cronos</h1>
        <p class="login-sub">Data Resilience Platform</p>
        {err && <div class="login-error">{err}</div>}
        <input class="input" placeholder="Username" value={user} onInput={(e: any) => setUser(e.target.value)} />
        <input class="input" type="password" placeholder="Password" value={pass} onInput={(e: any) => setPass(e.target.value)} />
        <button class="btn btn-primary" type="submit">Sign in</button>
      </form>
    </div>
  );
}

// Lazy page imports
import { OverviewPage } from './pages/overview';
import { JobsPage } from './pages/jobs';
import { MastersPage } from './pages/masters';
import { StoragePage } from './pages/storage';
import { CollectorsPage } from './pages/collectors';
