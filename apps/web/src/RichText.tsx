import { Fragment, type ReactNode } from 'react';

// Intentionally small Markdown subset. Raw HTML is always escaped by React.
function inline(value: string, onCitationClick?: (label: string) => void): ReactNode[] {
  return value.split(/(\*\*[^*]+\*\*|`[^`]+`|\[S\d+\])/g).map((part, i) =>
    part.startsWith('**') ? <strong key={i}>{part.slice(2, -2)}</strong> :
    part.startsWith('`') ? <code key={i}>{part.slice(1, -1)}</code> :
    /^\[S\d+\]$/.test(part) ? (
      <sup
        key={i}
        className="source-marker"
        onClick={() => onCitationClick?.(part.slice(1, -1))}
        title={`View citation ${part}`}
        style={onCitationClick ? { cursor: 'pointer' } : undefined}
      >
        {part.slice(1, -1)}
      </sup>
    ) :
    <Fragment key={i}>{part}</Fragment>);
}

export function RichText({ text, onCitationClick }: { text: string; onCitationClick?: (label: string) => void }) {
  const lines = text.split('\n');
  const elements: ReactNode[] = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line.trim()) continue;
    if (line.startsWith('```')) {
      const code = [];
      while (++i < lines.length && !lines[i].startsWith('```')) code.push(lines[i]);
      elements.push(<pre key={i}><code>{code.join('\n')}</code></pre>);
    } else if (/^#{1,6} /.test(line)) {
      elements.push(<h3 key={i}>{inline(line.replace(/^#{1,6} /, ''), onCitationClick)}</h3>);
    } else if (/^[-*] /.test(line)) {
      const items = [line.slice(2)];
      while (i + 1 < lines.length && /^[-*] /.test(lines[i + 1])) items.push(lines[++i].slice(2));
      elements.push(<ul key={i}>{items.map((item, n) => <li key={n}>{inline(item, onCitationClick)}</li>)}</ul>);
    } else if (/^\d+\. /.test(line)) {
      const items = [line.replace(/^\d+\. /, '')];
      while (i + 1 < lines.length && /^\d+\. /.test(lines[i + 1])) items.push(lines[++i].replace(/^\d+\. /, ''));
      elements.push(<ol key={i}>{items.map((item, n) => <li key={n}>{inline(item, onCitationClick)}</li>)}</ol>);
    } else if (line.startsWith('> ')) elements.push(<blockquote key={i}>{inline(line.slice(2), onCitationClick)}</blockquote>);
    else elements.push(<p key={i}>{inline(line, onCitationClick)}</p>);
  }
  return <div className="rich-text">{elements}</div>;
}

