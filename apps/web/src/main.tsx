import { useEffect, useRef, useState, type FormEvent } from 'react';
import { createRoot } from 'react-dom/client';
import { api, sourceUrl, type Artifact, type Detail, type Evidence, type Message, type Mode, type Session } from './api';
import { RichText } from './RichText';
import { ArtifactPreview } from './ArtifactPreview';
import './style.css';

const modes: {id: Mode; name: string; icon: string; hint: string}[] = [
  {id: 'qa', name: 'Ask & explore', icon: '↗', hint: 'Find the insight behind your next decision'},
  {id: 'ship30', name: 'Ship 30 essay', icon: '≋', hint: 'Turn evidence into a thoughtful, 1,250-word draft'},
  {id: 'html', name: 'Visual brief', icon: '▤', hint: 'Build a source-backed HTML document'},
  {id: 'markdown', name: 'Document', icon: '¶', hint: 'Create a reusable Markdown playbook'},
];
const starters = [
  {tag: 'PRODUCT–MARKET FIT', title: 'What tells us we’re ready to scale?', prompt: 'How should a B2B SaaS team evaluate product-market fit before scaling acquisition?'},
  {tag: 'ACTIVATION & RETENTION', title: 'Make the first experience count.', prompt: 'What should a product team consider when improving onboarding and activation?'},
  {tag: 'GROWTH STRATEGY', title: 'Find the next growth opportunity.', prompt: 'How should a growth team choose which experiments to prioritize?'},
];

function App() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [active, setActive] = useState<Detail | null>(null);
  const [mode, setMode] = useState<Mode>('qa');
  const [input, setInput] = useState('');
  const [provider, setProvider] = useState('ollama');
  const [providers, setProviders] = useState(['ollama']);
  const [model, setModel] = useState('');
  const [providerModels, setProviderModels] = useState<Record<string, string>>({});
  const [health, setHealth] = useState('Connecting');
  const [library, setLibrary] = useState<{episodes: number; chunks: number} | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [pending, setPending] = useState('');
  const [artifact, setArtifact] = useState<Artifact | null>(null);
  const [sources, setSources] = useState<Evidence[]>([]);
  const [panel, setPanel] = useState<'artifact' | 'evidence' | null>(null);
  const [code, setCode] = useState(false);
  const [sidebar, setSidebar] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const end = useRef<HTMLDivElement>(null);
  const composer = useRef<HTMLTextAreaElement>(null);
  const selection = useRef(0);

  async function refresh() {
    const results = await Promise.allSettled([
      api<Session[]>('/api/sessions'), api<{episodes: number; chunks: number}>('/api/library'),
      api<{provider: string; model: string; available_providers: string[]; provider_models: Record<string, string>}>('/config'),
      api<{status: string; ollama: string}>('/health'),
    ]);
    if (results[0].status === 'fulfilled') setSessions(results[0].value);
    if (results[1].status === 'fulfilled') setLibrary(results[1].value);
    if (results[2].status === 'fulfilled') {
      const value = results[2].value; setProvider(value.provider); setProviders(value.available_providers); setModel(value.model); setProviderModels(value.provider_models || {});
    }
    if (results[3].status === 'fulfilled') setHealth(results[3].value.status === 'ok' ? 'Ready' : results[3].value.ollama === 'missing_models' ? 'Model setup needed' : 'Service needs attention');
    else setHealth('API unavailable');
    const failure = results.find(result => result.status === 'rejected');
    if (failure?.status === 'rejected') setError(String(failure.reason.message));
  }
  useEffect(() => { void refresh(); }, []);
  useEffect(() => { end.current?.scrollIntoView({behavior: 'smooth'}); }, [active?.messages.length, busy]);
  useEffect(() => {
    if (!busy) { setElapsed(0); return; }
    const timer = setInterval(() => setElapsed(n => n + 1), 1000);
    return () => clearInterval(timer);
  }, [busy]);

  async function openSession(id: string) {
    if (busy) return;
    const token = ++selection.current;
    try {
      const detail = await api<Detail>(`/api/sessions/${id}`);
      if (token !== selection.current) return;
      setActive(detail); setPanel(null); setArtifact(null); setSources([]); setError(''); setSidebar(false);
    } catch (e) { setError((e as Error).message); }
  }
  function newConversation() {
    if (busy) return;
    selection.current++; setActive(null); setPanel(null); setError(''); setInput(''); setSidebar(false); composer.current?.focus();
  }
  async function send(event: FormEvent) {
    event.preventDefault();
    const content = input.trim();
    if (!content || busy) return;
    setBusy(true); setError(''); setPending(content); setInput('');
    let target = active;
    try {
      if (!target) {
        const created = await api<Session>('/api/sessions', {});
        target = {...created, messages: [], artifacts: []}; setActive(target);
        setSessions(previous => [created, ...previous]);
      }
      const reply = await api<{message: Message; artifact: Artifact | null}>(`/api/sessions/${target.id}/messages`, {content, mode, provider});
      const detail = await api<Detail>(`/api/sessions/${target.id}`);
      setActive(detail); setSessions(previous => previous.map(item => item.id === detail.id ? detail : item));
      setSources(reply.message.citations);
      if (reply.artifact) { setArtifact(reply.artifact); setPanel('artifact'); setCode(false); }
      else if (reply.message.citations.length) setPanel('evidence');
    } catch (e) { setError((e as Error).message); setInput(content); }
    finally { setBusy(false); setPending(''); composer.current?.focus(); }
  }
  function download() {
    if (!artifact) return;
    const blob = new Blob([artifact.content], {type: artifact.type === 'html' ? 'text/html' : 'text/markdown'});
    const url = URL.createObjectURL(blob); const anchor = document.createElement('a');
    anchor.href = url; anchor.download = `lenny-brief.${artifact.type === 'html' ? 'html' : 'md'}`; anchor.click(); URL.revokeObjectURL(url);
  }
  const hasMessages = !!active?.messages.length || busy;

  return <div className={`app ${panel ? 'with-panel' : ''}`}>
    <aside className={`sidebar ${sidebar ? 'mobile-open' : ''}`}>
      <div className="brand"><div className="brand-mark">L<span>↗</span></div><div>Lenny<span>GROWTH ASSISTANT</span></div></div>
      <button className="new-chat" onClick={newConversation} disabled={busy}><span>＋</span> New conversation <kbd>↗</kbd></button>
      <div className="nav-label">YOUR WORKSPACE</div>
      <div className="session-list">{sessions.length ? sessions.map(s => <button key={s.id} disabled={busy} onClick={() => void openSession(s.id)} className={`session ${s.id === active?.id ? 'selected' : ''}`}><span>◷</span>{s.title}</button>) : <p className="no-sessions">Good questions start here.<br/>Your conversations will appear here.</p>}</div>
      <div className="sidebar-note"><span className="tiny-spark">✳</span><p>A little less searching.<br/>A lot more perspective.</p></div>
      <div className="library-card"><span className="library-icon">▥</span><div>Transcript library<small>{library ? `${library.episodes} episodes · ${library.chunks.toLocaleString()} passages` : 'Waiting for the library'}</small></div></div>
      <div className="profile"><span>LG</span><div>Your growth workspace<small>Local-first · Source-backed</small></div></div>
    </aside>

    <main className="main">
      <header className="topbar"><div><button className="mobile-menu icon-button" onClick={() => setSidebar(!sidebar)} aria-label="Toggle conversations">☰</button><span className="breadcrumb">Workspace <span>/</span></span> {active ? 'Conversation' : 'New conversation'}</div><div className="connection"><span className={`status-dot ${health === 'Ready' ? 'ready' : ''}`}/>{health}<button className="icon-button" onClick={() => {setError(''); void refresh();}} aria-label="Refresh connection">↻</button></div></header>
      <div className="workspace-scroll">
        {!hasMessages ? <section className="welcome">
          <div className="eyebrow"><span/> FROM THE PODCAST. INTO PRACTICE.</div>
          <h1>Your next great decision<br/>starts with <em>a better question.</em></h1>
          <p className="intro">Explore the thinking of product and growth leaders.<br/>Find the evidence. Make it useful. Build something better.</p>
          <div className="mode-cards">{modes.slice(0, 3).map(item => <button key={item.id} className={`mode-card ${mode === item.id ? 'active' : ''}`} onClick={() => setMode(item.id)}><span className="mode-icon">{item.icon}</span><strong>{item.name}</strong><small>{item.hint}</small><span className="card-arrow">↗</span></button>)}</div>
          <div className="section-label">A FEW GOOD PLACES TO START <span>↙</span></div>
          <div className="starters">{starters.map(item => <button key={item.tag} onClick={() => {setInput(item.prompt); composer.current?.focus();}}><small>{item.tag}</small><span>{item.title}</span><b>↗</b></button>)}</div>
          {library?.episodes === 0 && <div className="setup-notice"><b>Your library is ready to be filled.</b> Import the transcript corpus to start asking grounded questions. Answers will use only indexed sources.</div>}
        </section> : <section className="messages" aria-label="Conversation">
          <div className="conversation-heading"><span className="eyebrow">EVIDENCE TO ACTION</span><h1>{active?.title === 'New conversation' ? pending : active?.title}</h1></div>
          {active?.messages.map(message => <article key={message.id} className={`message ${message.role}`}>
            <div className="message-avatar">{message.role === 'user' ? 'You' : 'L↗'}</div><div className="message-body"><div className="message-label">{message.role === 'user' ? 'You' : 'Lenny Growth Assistant'}{message.model && <small>{message.provider} · {message.model}</small>}</div>
              <RichText text={message.content}/>
              {message.status === 'draft_needs_review' && <div className="draft-warning">Draft needs review: outside the 1,100–1,400 word target.</div>}
              {!!message.citations.length && <div className="citations">{message.citations.map((source, i) => <button key={source.id} onClick={() => {setSources(message.citations); setPanel('evidence');}}><span>{source.label || `S${i + 1}`}</span>{source.guest} ↗</button>)}</div>}
              {active.artifacts.filter(a => a.message_id === message.id).map(a => <button className="artifact-link" key={a.id} onClick={() => {setArtifact(a); setSources(message.citations); setPanel('artifact'); setCode(false);}}><span>▤</span><div>{a.type === 'html' ? 'Visual brief' : 'Written document'}<small>Open in workspace</small></div><span>↗</span></button>)}
            </div>
          </article>)}
          {busy && <><article className="message user"><div className="message-avatar">You</div><div className="message-body"><div className="message-label">You</div><p>{pending}</p></div></article><div className="thinking" role="status"><span className="spinner"/><div>Searching sources and preparing your {mode === 'qa' ? 'answer' : 'draft'}…<small>{elapsed}s · Local models can take a few minutes. Source checks run before the answer appears.</small></div></div></>}
          <div ref={end}/>
        </section>}
      </div>
      <div className="composer-area">
        {error && <div role="alert" className="error"><span>{error}</span><button aria-label="Dismiss error" onClick={() => setError('')}>×</button></div>}
        <form className="composer" onSubmit={event => void send(event)}>
          <textarea ref={composer} value={input} onChange={e => setInput(e.target.value)} maxLength={6000} placeholder={mode === 'qa' ? 'What are you working through?' : 'What would you like to create?'} aria-label="Your question or request" rows={2} disabled={busy} onKeyDown={e => {if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {e.preventDefault(); e.currentTarget.form?.requestSubmit();}}}/>
          <div className="composer-tools"><div><select aria-label="Output type" value={mode} onChange={e => setMode(e.target.value as Mode)} disabled={busy}>{modes.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}</select><span className="tool-divider"/><select aria-label="Model provider" value={provider} onChange={e => {setProvider(e.target.value); setModel(providerModels[e.target.value] || '');}} disabled={busy}>{providers.map(p => <option key={p} value={p}>{p === 'ollama' ? '● Ollama · Local' : 'Anthropic · Cloud'}</option>)}</select></div><button className="send" disabled={busy || !input.trim()} aria-label="Send message">↑</button></div>
        </form>
        <div className="composer-footnote"><span>Every insight starts with a source.</span><span>{provider === 'ollama' ? model || 'Local inference' : `${model} · Context sent to Anthropic`} <span aria-hidden="true">·</span> Shift + Enter for a new line</span></div>
      </div>
    </main>

    {panel && <aside className="inspector" aria-label="Evidence and artifact workspace">
      <header><div className="panel-tabs"><button className={panel === 'evidence' ? 'active' : ''} onClick={() => setPanel('evidence')}>Evidence <span>{sources.length}</span></button>{artifact && <button className={panel === 'artifact' ? 'active' : ''} onClick={() => setPanel('artifact')}>Artifact</button>}</div><button className="icon-button" onClick={() => setPanel(null)} aria-label="Close workspace">×</button></header>
      {panel === 'evidence' ? <div className="evidence-content"><div className="eyebrow">GO TO THE SOURCE</div><h2>Good advice.<br/><em>With receipts.</em></h2><p className="panel-intro">The passages behind this answer. Inspect the context before putting an idea into practice.</p>{sources.map((source, i) => <article className="evidence-card" key={source.id}><div className="evidence-top"><span>{source.label || `S${i + 1}`}</span><small>TRANSCRIPT EXCERPT</small></div><h3>{source.title}</h3><p className="guest">{source.guest}</p><blockquote>{source.excerpt}</blockquote>{sourceUrl(source.url) && <a target="_blank" rel="noopener noreferrer" href={sourceUrl(source.url)}>Open original source ↗</a>}</article>)}{!sources.length && <p>No sources for this response.</p>}<p className="evidence-note">Citations identify retrieved passages. Review whether they support each claim; a citation alone is not a fact check.</p></div> : artifact && <div className="artifact-content"><div className="artifact-toolbar"><strong>{artifact.type === 'html' ? 'Visual brief' : 'Document'}</strong><div><button onClick={() => setCode(!code)}>{code ? 'Preview' : 'Source'}</button><button onClick={download}>Export ↗</button></div></div>{code ? <pre className="raw-source">{artifact.content}</pre> : artifact.type === 'html' ? <ArtifactPreview title={artifact.title} html={artifact.content}/> : <div className="document"><RichText text={artifact.content}/></div>}<footer>Source-backed draft · Review before sharing</footer></div>}
    </aside>}
  </div>;
}

createRoot(document.getElementById('root')!).render(<App/>);
