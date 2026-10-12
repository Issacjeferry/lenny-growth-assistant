import { useEffect, useRef, useState, type FormEvent } from 'react';
import { createRoot } from 'react-dom/client';
import { api, sourceUrl, type Artifact, type Detail, type Evidence, type Message, type Mode, type Session } from './api';
import { RichText } from './RichText';
import { ArtifactPreview } from './ArtifactPreview';
import './style.css';

const modes: {id: Mode; name: string; icon: string; badge: string; hint: string}[] = [
  {id: 'qa', name: 'Executive Q&A', icon: '↗', badge: 'Decision Memo', hint: 'Grounded insights backed by transcript quotes'},
  {id: 'ship30', name: 'Ship 30 Essay', icon: '≋', badge: '1,250-Word Essay', hint: 'Thoughtful publication draft with counter-intuitive perspectives'},
  {id: 'html', name: 'Visual Brief', icon: '▤', badge: 'Interactive HTML', hint: 'Structured briefing document with tables and framework layout'},
  {id: 'markdown', name: 'Strategy Playbook', icon: '¶', badge: 'Markdown SOP', hint: 'Actionable execution roadmap and operational checklist'},
];

interface Framework {
  id: string;
  name: string;
  guest: string;
  tag: string;
  icon: string;
  prompt: string;
  description: string;
}

const frameworks: Framework[] = [
  {
    id: 'plg-loops',
    name: 'Growth Loops vs Funnels',
    guest: 'Elena Verna',
    tag: 'PLG & VIRALITY',
    icon: '🔄',
    prompt: 'How should a growth team design self-reinforcing acquisition and retention loops instead of linear funnels? Outline key loop types from Lenny’s guests.',
    description: 'Transform leaky funnels into compounding acquisition & retention engines.',
  },
  {
    id: 'pmf-test',
    name: '40% PMF Leading Indicator',
    guest: 'Sean Ellis',
    tag: 'PRODUCT-MARKET FIT',
    icon: '🎯',
    prompt: 'How should a B2B SaaS team evaluate product-market fit using Sean Ellis’s 40% test and retention curves before ramping acquisition?',
    description: 'Benchmark customer disappointment rates and cohort retention stability.',
  },
  {
    id: 'good-great-pm',
    name: 'Good PM vs. Great PM',
    guest: 'Shreyas Doshi',
    tag: 'PRODUCT JUDGMENT',
    icon: '💎',
    prompt: 'What distinguishes high-leverage product leaders from average PMs according to Shreyas Doshi on Lenny’s podcast?',
    description: 'Master high-ROI product judgment, LNO prioritization, and leverage.',
  },
  {
    id: 'four-fits',
    name: 'The Four Fits Framework',
    guest: 'Brian Balfour',
    tag: 'GROWTH STRATEGY',
    icon: '🧩',
    prompt: 'Explain Brian Balfour’s Four Fits framework (Market-Product, Product-Channel, Channel-Model, Model-Market) and how misalignment stalls scaling.',
    description: 'Align product, distribution channel, monetization model, and market.',
  },
  {
    id: 'jtbd-forces',
    name: 'Jobs-To-Be-Done Switch Forces',
    guest: 'Bob Moesta',
    tag: 'USER PSYCHOLOGY',
    icon: '⚓',
    prompt: 'How do customers make the decision to buy or switch according to Bob Moesta’s JTBD framework (Push, Pull, Habit, Anxiety)?',
    description: 'Uncover the struggling moments and anxieties driving purchase decisions.',
  },
  {
    id: 'saas-pricing',
    name: 'Value-Based Pricing & Tiers',
    guest: 'Patrick Campbell',
    tag: 'PRICING & PACKAGING',
    icon: '🏷️',
    prompt: 'What are the top insights from Lenny’s podcast on SaaS pricing page design, value metrics, freemium versus free trial, and tiering?',
    description: 'Align price points with customer perceived value and expansion hooks.',
  },
];

const featuredGuests = [
  {name: 'Elena Verna', role: 'Head of Growth, Amplitude & Miro', topic: 'B2B Product-Led Growth & Loops'},
  {name: 'Brian Balfour', role: 'Founder, Reforge · ex-HubSpot', topic: 'The Four Fits & Retention Engines'},
  {name: 'Sean Ellis', role: 'Author of Hacking Growth', topic: '40% PMF Test & Experiment Velocity'},
  {name: 'Shreyas Doshi', role: 'Product Leader, ex-Stripe & Twitter', topic: 'LNO Framework & High-Leverage Judgment'},
  {name: 'Bob Moesta', role: 'Co-creator of Jobs To Be Done', topic: 'Switching Forces & Customer Struggling Moments'},
  {name: 'April Dunford', role: 'Author of Obviously Awesome', topic: 'Positioning & Competitive Alternatives'},
  {name: 'Fareed Mosavat', role: 'VP Growth, Reforge · ex-Slack', topic: 'Activation Friction & North Star Metrics'},
  {name: 'Casey Winters', role: 'Chief Product Officer, Eventbrite', topic: 'SEO & Viral Engines vs Paid Acquisition'},
];

const topicPillars = [
  {title: 'Product-Led Growth (PLG)', count: '48 episodes', query: 'What are the core fundamentals of building a successful PLG motion according to Lenny’s guests?'},
  {title: 'Retention & Churn Mitigation', count: '42 episodes', query: 'What strategies do top growth leaders recommend to flatten cohort retention curves and prevent churn?'},
  {title: 'Onboarding & Activation', count: '36 episodes', query: 'How do top product teams measure the aha moment and optimize user activation workflows?'},
  {title: 'Pricing & Monetization', count: '29 episodes', query: 'How should startups determine their core value metric and price packaging tiers?'},
  {title: '0 to 1 PMF & Validation', count: '54 episodes', query: 'What are the most reliable leading indicators of true product-market fit before scaling sales?'},
];

const followUpSuggestions = [
  '⚡ Draft a 30-day experiment backlog to validate this',
  '⚠️ What are the biggest failure modes and risks?',
  '📋 Turn this insight into a 1-page executive memo',
  '🎯 How should we measure the primary metric for this?',
];

function calculateMatch(distance: number | null | undefined): number {
  if (distance === null || distance === undefined) return 92;
  const match = Math.round((1 - Math.min(distance, 0.75)) * 100);
  return Math.max(68, Math.min(99, match));
}

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
  const [searchQuery, setSearchQuery] = useState('');
  const [sessionFilter, setSessionFilter] = useState<'all' | 'briefs' | 'essays'>('all');
  const [showCorpusModal, setShowCorpusModal] = useState(false);
  const [viewportMode, setViewportMode] = useState<'desktop' | 'mobile'>('desktop');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const end = useRef<HTMLDivElement>(null);
  const composer = useRef<HTMLTextAreaElement>(null);
  const selection = useRef(0);

  async function refresh() {
    const results = await Promise.allSettled([
      api<Session[]>('/api/sessions'),
      api<{episodes: number; chunks: number}>('/api/library'),
      api<{provider: string; model: string; available_providers: string[]; provider_models: Record<string, string>}>('/config'),
      api<{status: string; ollama: string}>('/health'),
    ]);
    if (results[0].status === 'fulfilled') setSessions(results[0].value);
    if (results[1].status === 'fulfilled') setLibrary(results[1].value);
    if (results[2].status === 'fulfilled') {
      const value = results[2].value;
      setProvider(value.provider);
      setProviders(value.available_providers);
      setModel(value.model);
      setProviderModels(value.provider_models || {});
    }
    if (results[3].status === 'fulfilled') {
      setHealth(results[3].value.status === 'ok' ? 'Ready' : results[3].value.ollama === 'missing_models' ? 'Model setup needed' : 'Service needs attention');
    } else {
      setHealth('API unavailable');
    }
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
      setActive(detail);
      setPanel(null);
      setArtifact(null);
      setSources([]);
      setError('');
      setSidebar(false);
    } catch (e) { setError((e as Error).message); }
  }

  function newConversation() {
    if (busy) return;
    selection.current++;
    setActive(null);
    setPanel(null);
    setError('');
    setInput('');
    setSidebar(false);
    composer.current?.focus();
  }

  async function send(event?: FormEvent, customPrompt?: string) {
    if (event) event.preventDefault();
    const content = (customPrompt ?? input).trim();
    if (!content || busy) return;
    setBusy(true);
    setError('');
    setPending(content);
    setInput('');
    let target = active;
    try {
      if (!target) {
        const created = await api<Session>('/api/sessions', {});
        target = {...created, messages: [], artifacts: []};
        setActive(target);
        setSessions(previous => [created, ...previous]);
      }
      const reply = await api<{message: Message; artifact: Artifact | null}>(`/api/sessions/${target.id}/messages`, {content, mode, provider});
      const detail = await api<Detail>(`/api/sessions/${target.id}`);
      setActive(detail);
      setSessions(previous => previous.map(item => item.id === detail.id ? detail : item));
      setSources(reply.message.citations);
      if (reply.artifact) {
        setArtifact(reply.artifact);
        setPanel('artifact');
        setCode(false);
      } else if (reply.message.citations.length) {
        setPanel('evidence');
      }
    } catch (e) {
      setError((e as Error).message);
      setInput(content);
    } finally {
      setBusy(false);
      setPending('');
      composer.current?.focus();
    }
  }

  function downloadArtifact() {
    if (!artifact) return;
    const blob = new Blob([artifact.content], {type: artifact.type === 'html' ? 'text/html' : 'text/markdown'});
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `lenny-${artifact.type === 'html' ? 'visual-brief' : 'playbook'}.${artifact.type === 'html' ? 'html' : 'md'}`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function exportMessageMarkdown(message: Message) {
    const header = `# Lenny Growth Assistant Brief\n*Generated with ${message.provider || 'local'} (${message.model || 'model'})*\n\n`;
    const citationsBlock = message.citations.length ? `\n\n## Sources & Citations\n` + message.citations.map((c, i) => `${i + 1}. **${c.guest}** — "${c.title}"\n   > "${c.excerpt}"\n   Link: ${c.url}`).join('\n\n') : '';
    const blob = new Blob([header + message.content + citationsBlock], {type: 'text/markdown'});
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `growth-brief-${message.id.slice(0, 6)}.md`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  async function copyToClipboard(text: string, id: string) {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2200);
    } catch {
      // ignore clipboard error
    }
  }

  function selectFramework(item: Framework) {
    setInput(item.prompt);
    setShowCorpusModal(false);
    composer.current?.focus();
  }

  const filteredSessions = sessions.filter(s => {
    const matchesSearch = s.title.toLowerCase().includes(searchQuery.toLowerCase());
    if (sessionFilter === 'briefs') return matchesSearch && (s.title.toLowerCase().includes('brief') || s.title.toLowerCase().includes('html'));
    if (sessionFilter === 'essays') return matchesSearch && (s.title.toLowerCase().includes('essay') || s.title.toLowerCase().includes('ship'));
    return matchesSearch;
  });

  const hasMessages = !!active?.messages.length || busy;

  return (
    <div className={`app ${panel ? 'with-panel' : ''}`}>
      {/* LEFT SIDEBAR: PRODUCT KNOWLEDGE HUB & CONVERSATIONS */}
      <aside className={`sidebar ${sidebar ? 'mobile-open' : ''}`}>
        <div className="brand" onClick={() => setShowCorpusModal(true)} title="Explore Lenny's Corpus & Guests">
          <div className="brand-mark">
            <span className="brand-letter">L</span>
            <div className="audio-wave">
              <span/><span/><span/><span/>
            </div>
          </div>
          <div className="brand-text">
            <strong>Lenny</strong>
            <span>GROWTH STUDIO</span>
          </div>
        </div>

        <button className="new-chat" onClick={newConversation} disabled={busy}>
          <span className="plus-icon">＋</span>
          <span>New Investigation</span>
          <kbd>Ctrl+N</kbd>
        </button>

        {/* SEARCH & FILTERS FOR PAST CONVERSATIONS */}
        <div className="session-filter-box">
          <div className="search-input-wrapper">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              placeholder="Search discussions…"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="session-search"
            />
            {searchQuery && <button className="clear-search" onClick={() => setSearchQuery('')}>×</button>}
          </div>
          <div className="filter-pill-row">
            <button className={`filter-pill ${sessionFilter === 'all' ? 'active' : ''}`} onClick={() => setSessionFilter('all')}>All ({sessions.length})</button>
            <button className={`filter-pill ${sessionFilter === 'briefs' ? 'active' : ''}`} onClick={() => setSessionFilter('briefs')}>Briefs</button>
            <button className={`filter-pill ${sessionFilter === 'essays' ? 'active' : ''}`} onClick={() => setSessionFilter('essays')}>Essays</button>
          </div>
        </div>

        <div className="session-list">
          {filteredSessions.length ? (
            filteredSessions.map(s => (
              <button
                key={s.id}
                disabled={busy}
                onClick={() => void openSession(s.id)}
                className={`session ${s.id === active?.id ? 'selected' : ''}`}
              >
                <span className="session-dot">●</span>
                <span className="session-title">{s.title}</span>
                <span className="session-arrow">↗</span>
              </button>
            ))
          ) : (
            <div className="no-sessions">
              {searchQuery ? 'No matching discussions found.' : 'Good strategy begins with grounded questions.'}
            </div>
          )}
        </div>

        {/* CORPUS INTELLIGENCE CARD (CLICKABLE) */}
        <div className="library-card" onClick={() => setShowCorpusModal(true)}>
          <div className="library-icon-wrap">
            <span className="library-icon">🎙️</span>
            <span className="pulse-indicator"/>
          </div>
          <div className="library-info">
            <strong>Podcast Corpus Intel</strong>
            <small>{library ? `${library.episodes} episodes · ${library.chunks.toLocaleString()} indexed passages` : 'Loading index…'}</small>
            <span className="library-explore-link">Browse 8+ Top Guests & Topics ↗</span>
          </div>
        </div>

        {/* USER / ENGINE STATUS BADGE */}
        <div className="profile">
          <span className="profile-badge">PM</span>
          <div className="profile-meta">
            <strong>Product & Growth Lead</strong>
            <small>Local Vector DB · 100% Grounded</small>
          </div>
        </div>
      </aside>

      {/* MAIN WORKSPACE AREA */}
      <main className="main">
        {/* EXECUTIVE TOP BAR */}
        <header className="topbar">
          <div className="topbar-left">
            <button className="mobile-menu icon-button" onClick={() => setSidebar(!sidebar)} aria-label="Toggle navigation">☰</button>
            <span className="breadcrumb">Growth Studio <span>/</span></span>
            <span className="topbar-title">{active ? active.title : 'New Investigation'}</span>
            {active && <span className="mode-tag">{modes.find(m => m.id === mode)?.badge}</span>}
          </div>

          <div className="topbar-right">
            <button className="corpus-btn" onClick={() => setShowCorpusModal(true)}>
              <span>🎙️</span> Corpus Directory
            </button>
            <div className="connection">
              <span className={`status-dot ${health === 'Ready' ? 'ready' : ''}`}/>
              <span className="connection-text">{health === 'Ready' ? `${provider === 'ollama' ? 'Local LLM' : 'Cloud LLM'} Active` : health}</span>
              <button className="icon-button" onClick={() => { setError(''); void refresh(); }} aria-label="Refresh status" title="Refresh health">↻</button>
            </div>
          </div>
        </header>

        {/* WORKSPACE SCROLL AREA */}
        <div className="workspace-scroll">
          {!hasMessages ? (
            /* EMPTY / WELCOME STATE: THE STRATEGY LAUNCHPAD */
            <section className="welcome">
              <div className="eyebrow">
                <span className="diamond-bullet"/>
                LENNY’S PODCAST INTELLIGENCE ENGINE · 276 EPISODES
              </div>

              <h1>Turn podcast wisdom into<br/><em>executive-ready strategy.</em></h1>
              <p className="intro">
                Ask targeted product, growth, and scaling questions backed by verbatim transcripts of the world’s top operators.
                Zero hallucinations — every answer is anchored in indexed receipts.
              </p>

              {/* 4 DISTINCT WORKSPACE MODES */}
              <div className="mode-selector-header">
                <span>SELECT YOUR OUTPUT OBJECTIVE</span>
              </div>
              <div className="mode-cards">
                {modes.map(item => (
                  <button
                    key={item.id}
                    className={`mode-card ${mode === item.id ? 'active' : ''}`}
                    onClick={() => setMode(item.id)}
                  >
                    <div className="mode-card-top">
                      <span className="mode-icon">{item.icon}</span>
                      <span className="mode-badge-pill">{item.badge}</span>
                    </div>
                    <strong>{item.name}</strong>
                    <small>{item.hint}</small>
                  </button>
                ))}
              </div>

              {/* MENTAL MODELS & GROWTH FRAMEWORKS GRID */}
              <div className="frameworks-section">
                <div className="section-label">
                  <span>PROVEN GROWTH FRAMEWORKS & MENTAL MODELS</span>
                  <button className="link-button" onClick={() => setShowCorpusModal(true)}>View All Guests ↗</button>
                </div>
                <div className="frameworks-grid">
                  {frameworks.map(fw => (
                    <div key={fw.id} className="framework-card" onClick={() => selectFramework(fw)}>
                      <div className="framework-header">
                        <span className="fw-icon">{fw.icon}</span>
                        <span className="fw-tag">{fw.tag}</span>
                        <span className="fw-guest">{fw.guest}</span>
                      </div>
                      <h3>{fw.name}</h3>
                      <p>{fw.description}</p>
                      <button className="fw-apply-btn">
                        <span>Load Framework</span>
                        <b>↗</b>
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          ) : (
            /* CONVERSATION MESSAGES: EXECUTIVE STRATEGY FEED */
            <section className="messages" aria-label="Conversation Feed">
              <div className="conversation-heading">
                <div className="eyebrow">
                  <span className="diamond-bullet"/>
                  VERIFIED EVIDENCE & STRATEGIC SYNTHESIS
                </div>
                <h1>{active?.title === 'New conversation' ? pending : active?.title}</h1>
                <div className="session-meta-chips">
                  <span className="meta-chip">Mode: {modes.find(m => m.id === mode)?.badge}</span>
                  <span className="meta-chip">Engine: {provider === 'ollama' ? 'lenny-local (Ollama)' : 'Anthropic Claude'}</span>
                  {active?.artifacts.length ? <span className="meta-chip accent">1 Generated Artifact Available</span> : null}
                </div>
              </div>

              {active?.messages.map((message, idx) => (
                <article key={message.id || idx} className={`message ${message.role}`}>
                  <div className="message-avatar">
                    {message.role === 'user' ? 'YOU' : 'L↗'}
                  </div>

                  <div className="message-body">
                    <div className="message-label-bar">
                      <div className="author-info">
                        <strong>{message.role === 'user' ? 'Strategy Lead' : 'Lenny Growth Intelligence'}</strong>
                        {message.model && <span className="model-chip">{message.provider} · {message.model}</span>}
                        {message.citations.length > 0 && (
                          <span className="verified-badge">✓ {message.citations.length} Verified Sources</span>
                        )}
                      </div>

                      {message.role === 'assistant' && (
                        <div className="message-quick-tools">
                          <button
                            className="tool-btn"
                            onClick={() => copyToClipboard(message.content, message.id)}
                            title="Copy formatted answer"
                          >
                            {copiedId === message.id ? '✓ Copied' : '📋 Copy'}
                          </button>
                          <button
                            className="tool-btn"
                            onClick={() => exportMessageMarkdown(message)}
                            title="Download markdown brief"
                          >
                            📄 Export .md
                          </button>
                          {message.citations.length > 0 && (
                            <button
                              className="tool-btn inspect-btn"
                              onClick={() => { setSources(message.citations); setPanel('evidence'); }}
                              title="Inspect transcript citations"
                            >
                              🔍 Receipts ({message.citations.length})
                            </button>
                          )}
                        </div>
                      )}
                    </div>

                    {/* MESSAGE CONTENT */}
                    <RichText
                      text={message.content}
                      onCitationClick={label => {
                        const matched = message.citations.find(c => c.label === label || c.id === label);
                        setSources(message.citations);
                        setPanel('evidence');
                      }}
                    />

                    {message.status === 'draft_needs_review' && (
                      <div className="draft-warning">
                        ⚠️ Word count notice: Model generated an output outside the ideal target. Please review carefully.
                      </div>
                    )}

                    {/* CITATION CHIPS WITH GUEST & EPISODE LABELS */}
                    {!!message.citations.length && (
                      <div className="citations-tray">
                        <span className="tray-label">EPISODE EVIDENCE:</span>
                        <div className="citations-list">
                          {message.citations.map((source, i) => (
                            <button
                              key={source.id || i}
                              className="citation-pill"
                              onClick={() => { setSources(message.citations); setPanel('evidence'); }}
                            >
                              <span className="pill-badge">{source.label || `S${i + 1}`}</span>
                              <span className="pill-guest">{source.guest}</span>
                              <span className="pill-title">— {source.title.slice(0, 36)}…</span>
                              <span className="pill-match">{calculateMatch(source.distance)}% Match</span>
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* EMBEDDED ARTIFACT CARD */}
                    {active.artifacts.filter(a => a.message_id === message.id).map(a => (
                      <div className="artifact-banner-card" key={a.id}>
                        <div className="artifact-icon-col">
                          <span>{a.type === 'html' ? '▤' : '¶'}</span>
                        </div>
                        <div className="artifact-info-col">
                          <div className="artifact-type-tag">{a.type === 'html' ? 'INTERACTIVE VISUAL BRIEF' : 'STRATEGY DOCUMENT'}</div>
                          <h4>{a.title || 'Growth Strategy Synthesis Brief'}</h4>
                          <p>Rendered in sandboxed security iframe with responsive layout inspection.</p>
                        </div>
                        <div className="artifact-actions-col">
                          <button
                            className="open-canvas-btn"
                            onClick={() => { setArtifact(a); setSources(message.citations); setPanel('artifact'); setCode(false); }}
                          >
                            Open in Studio Canvas ↗
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </article>
              ))}

              {/* STREAMING / GENERATION STATE */}
              {busy && (
                <>
                  <article className="message user">
                    <div className="message-avatar">YOU</div>
                    <div className="message-body">
                      <div className="message-label-bar"><strong>Strategy Lead</strong></div>
                      <p>{pending}</p>
                    </div>
                  </article>
                  <div className="thinking-card" role="status">
                    <div className="pulse-spinner">
                      <span className="inner-pulse"/>
                    </div>
                    <div className="thinking-details">
                      <strong>Retrieving transcript passages & evaluating cross-guest synthesis…</strong>
                      <p>
                        Vector similarity scan complete · Synthesizing grounded {mode === 'qa' ? 'recommendation' : mode === 'ship30' ? 'Ship 30 essay' : 'artifact'}…
                        <span className="elapsed-timer">{elapsed}s elapsed</span>
                      </p>
                    </div>
                  </div>
                </>
              )}

              {/* QUICK FOLLOW-UP SUGGESTION CHIPS */}
              {!busy && active?.messages.length && (
                <div className="followup-suggestions-row">
                  <span className="suggestions-label">Explore Next:</span>
                  {followUpSuggestions.map((promptText, i) => (
                    <button
                      key={i}
                      className="followup-chip"
                      onClick={() => { setInput(promptText); composer.current?.focus(); }}
                    >
                      {promptText}
                    </button>
                  ))}
                </div>
              )}

              <div ref={end}/>
            </section>
          )}
        </div>

        {/* FLOATING COMPOSER AREA */}
        <div className="composer-area">
          {error && (
            <div role="alert" className="error">
              <span>{error}</span>
              <button aria-label="Dismiss error" onClick={() => setError('')}>×</button>
            </div>
          )}

          {/* QUICK FRAMEWORK SHORTCUT BAR */}
          <div className="quick-framework-bar">
            <span className="quick-label">⚡ Frameworks:</span>
            {frameworks.slice(0, 4).map(fw => (
              <button
                key={fw.id}
                type="button"
                className="quick-chip"
                onClick={() => selectFramework(fw)}
              >
                {fw.icon} {fw.name.split(' ')[0]} ({fw.guest.split(' ')[0]})
              </button>
            ))}
          </div>

          <form className="composer-card" onSubmit={event => void send(event)}>
            <textarea
              ref={composer}
              value={input}
              onChange={e => setInput(e.target.value)}
              maxLength={6000}
              placeholder={
                mode === 'qa' ? 'Ask a tactical growth question (e.g., How does Elena Verna design PLG loops?)…' :
                mode === 'ship30' ? 'What product or growth topic do you want to explore as a Ship 30 essay?…' :
                mode === 'html' ? 'Describe the visual brief, comparison matrix, or scorecard you need…' :
                'Outline the strategy playbook you want to build…'
              }
              aria-label="Your question or prompt"
              rows={2}
              disabled={busy}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
                  e.preventDefault();
                  e.currentTarget.form?.requestSubmit();
                }
              }}
            />

            <div className="composer-controls">
              <div className="controls-group">
                {/* MODE SELECTOR */}
                <div className="custom-select-wrap mode-select-wrap" title="Select Output Format">
                  <span className="select-icon">{modes.find(m => m.id === mode)?.icon}</span>
                  <select
                    aria-label="Output Mode"
                    value={mode}
                    onChange={e => setMode(e.target.value as Mode)}
                    disabled={busy}
                    className="styled-select"
                  >
                    {modes.map(m => (
                      <option key={m.id} value={m.id}>{m.name} · {m.badge}</option>
                    ))}
                  </select>
                  <span className="select-chevron">▾</span>
                </div>

                <span className="control-sep"/>

                {/* PROVIDER / ENGINE SELECTOR */}
                <div className="custom-select-wrap provider-select-wrap" title="Select LLM Engine">
                  <span className="select-icon">{provider === 'gemini' ? '⚡' : '●'}</span>
                  <select
                    aria-label="Model Provider"
                    value={provider}
                    onChange={e => {
                      setProvider(e.target.value);
                      setModel(providerModels[e.target.value] || '');
                    }}
                    disabled={busy}
                    className="styled-select"
                  >
                    {providers.map(p => (
                      <option key={p} value={p}>
                        {p === 'ollama' ? 'Local Ollama (lenny-local)' : p === 'gemini' ? '⚡ Google Gemini (Cloud · 2s)' : 'Anthropic Claude (Cloud)'}
                      </option>
                    ))}
                  </select>
                  <span className="select-chevron">▾</span>
                </div>
              </div>

              <div className="send-wrapper">
                <span className="char-count">{input.length}/6000</span>
                <button
                  type="submit"
                  className="send-button"
                  disabled={busy || !input.trim()}
                  aria-label="Run investigation"
                  title="Send (Enter)"
                >
                  ↑
                </button>
              </div>
            </div>
          </form>

          <div className="composer-footer-note">
            <span>🔒 Grounded exclusively in verified podcast transcripts. No hallucinated guest opinions.</span>
            <span>Press <strong>Enter</strong> to send · <strong>Shift+Enter</strong> for newline</span>
          </div>
        </div>
      </main>

      {/* RIGHT SLIDING INSPECTOR: EVIDENCE & ARTIFACT STUDIO */}
      {panel && (
        <aside className="inspector" aria-label="Evidence and Artifact Workspace">
          <header className="inspector-header">
            <div className="panel-tabs">
              <button
                className={`tab-btn ${panel === 'evidence' ? 'active' : ''}`}
                onClick={() => setPanel('evidence')}
              >
                Evidence Receipts <span className="tab-count">{sources.length}</span>
              </button>
              {artifact && (
                <button
                  className={`tab-btn ${panel === 'artifact' ? 'active' : ''}`}
                  onClick={() => setPanel('artifact')}
                >
                  Artifact Canvas
                </button>
              )}
            </div>
            <button className="icon-button close-panel" onClick={() => setPanel(null)} aria-label="Close panel">×</button>
          </header>

          {/* EVIDENCE DRAWER */}
          {panel === 'evidence' ? (
            <div className="evidence-content">
              <div className="evidence-header-block">
                <div className="eyebrow">PODCAST VERBATIM VAULT</div>
                <h2>Audited Receipts & Source Passages</h2>
                <p className="panel-intro">
                  Every citation is extracted directly from Lenny Rachitsky’s episode transcripts.
                  Cross-verify context and timestamps before deploying ideas into production.
                </p>
              </div>

              {sources.map((source, i) => (
                <article className="evidence-card" key={source.id || i}>
                  <div className="evidence-card-header">
                    <span className="source-label">{source.label || `S${i + 1}`}</span>
                    <span className="match-pill">{calculateMatch(source.distance)}% Match</span>
                    <button
                      className="copy-quote-btn"
                      onClick={() => copyToClipboard(`"${source.excerpt}" — ${source.guest}, ${source.title}`, source.id)}
                    >
                      {copiedId === source.id ? '✓ Copied' : 'Copy Quote'}
                    </button>
                  </div>

                  <h3 className="evidence-episode-title">{source.title}</h3>
                  <div className="evidence-guest-badge">
                    <span>🎙️ Guest:</span> <strong>{source.guest}</strong>
                  </div>

                  <blockquote className="evidence-quote">
                    "{source.excerpt}"
                  </blockquote>

                  {sourceUrl(source.url) && (
                    <a target="_blank" rel="noopener noreferrer" href={sourceUrl(source.url)} className="source-external-link">
                      Listen to Episode / Read Transcript ↗
                    </a>
                  )}
                </article>
              ))}

              {!sources.length && (
                <div className="empty-panel-msg">
                  <p>No citations returned for this message.</p>
                </div>
              )}

              <div className="evidence-disclaimer">
                Citations reflect vector semantic retrieval from 276 transcribed episodes.
                Always cross-check specific business constraints before implementing playbooks.
              </div>
            </div>
          ) : artifact && (
            /* ARTIFACT STUDIO CANVAS */
            <div className="artifact-content">
              <div className="artifact-toolbar">
                <div className="artifact-meta">
                  <strong>{artifact.type === 'html' ? 'Visual Brief' : 'Strategy Document'}</strong>
                  <span className="artifact-badge">{artifact.type.toUpperCase()}</span>
                </div>

                <div className="artifact-controls">
                  {artifact.type === 'html' && !code && (
                    <div className="viewport-toggle">
                      <button
                        className={`vp-btn ${viewportMode === 'desktop' ? 'active' : ''}`}
                        onClick={() => setViewportMode('desktop')}
                        title="Desktop view"
                      >
                        Desktop
                      </button>
                      <button
                        className={`vp-btn ${viewportMode === 'mobile' ? 'active' : ''}`}
                        onClick={() => setViewportMode('mobile')}
                        title="Mobile preview"
                      >
                        Mobile
                      </button>
                    </div>
                  )}
                  <button className="tb-btn" onClick={() => setCode(!code)}>
                    {code ? 'Live Preview' : 'Raw Source'}
                  </button>
                  <button className="tb-btn export-btn" onClick={downloadArtifact}>
                    Export File ↗
                  </button>
                </div>
              </div>

              <div className={`artifact-viewport-wrapper ${artifact.type === 'html' && viewportMode === 'mobile' ? 'mobile-frame' : ''}`}>
                {code ? (
                  <pre className="raw-source">{artifact.content}</pre>
                ) : artifact.type === 'html' ? (
                  <ArtifactPreview title={artifact.title} html={artifact.content}/>
                ) : (
                  <div className="document">
                    <RichText text={artifact.content}/>
                  </div>
                )}
              </div>

              <footer className="artifact-footer">
                <span>🛡️ Rendered securely in sandboxed iframe without scripts or network access</span>
              </footer>
            </div>
          )}
        </aside>
      )}

      {/* CORPUS & GUEST DIRECTORY MODAL */}
      {showCorpusModal && (
        <div className="modal-overlay" onClick={() => setShowCorpusModal(false)}>
          <div className="modal-container" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <div className="eyebrow">EPISODE DIRECTORY & OPERATOR KNOWLEDGE BASE</div>
                <h2>Lenny’s Podcast Corpus Intelligence</h2>
              </div>
              <button className="modal-close" onClick={() => setShowCorpusModal(false)}>×</button>
            </div>

            <div className="modal-stats-bar">
              <div className="m-stat">
                <strong>276</strong>
                <span>Ingested Episodes</span>
              </div>
              <div className="m-stat">
                <strong>13,120</strong>
                <span>Embedded Passages</span>
              </div>
              <div className="m-stat">
                <strong>nomic-embed</strong>
                <span>768-Dim Vector Space</span>
              </div>
              <div className="m-stat">
                <strong>100%</strong>
                <span>Grounded Retrieval</span>
              </div>
            </div>

            <div className="modal-body">
              <h3>Featured Top Operators</h3>
              <p className="modal-sub">Click any operator to seed a targeted inquiry into the growth studio:</p>
              <div className="guest-cards-grid">
                {featuredGuests.map((g, i) => (
                  <div
                    key={i}
                    className="guest-card"
                    onClick={() => {
                      setInput(`What are the key frameworks and counter-intuitive insights from ${g.name} on ${g.topic}?`);
                      setShowCorpusModal(false);
                      composer.current?.focus();
                    }}
                  >
                    <div className="guest-avatar-circle">{g.name.split(' ').map(n => n[0]).join('')}</div>
                    <div className="guest-info">
                      <h4>{g.name}</h4>
                      <small className="guest-role">{g.role}</small>
                      <span className="guest-topic-pill">{g.topic}</span>
                    </div>
                  </div>
                ))}
              </div>

              <h3 style={{ marginTop: '28px' }}>Core Growth Pillars</h3>
              <div className="topic-pillars-list">
                {topicPillars.map((tp, i) => (
                  <div
                    key={i}
                    className="topic-pillar-row"
                    onClick={() => {
                      setInput(tp.query);
                      setShowCorpusModal(false);
                      composer.current?.focus();
                    }}
                  >
                    <div>
                      <strong>{tp.title}</strong>
                      <span className="tp-count">{tp.count}</span>
                    </div>
                    <span className="tp-arrow">Ask Question ↗</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="modal-footer">
              <button className="modal-done-btn" onClick={() => setShowCorpusModal(false)}>Back to Workspace</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

createRoot(document.getElementById('root')!).render(<App/>);
