import { describe, expect, it, vi, afterEach } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { RichText } from './RichText';
import { ArtifactPreview } from './ArtifactPreview';
import { api, sourceUrl } from './api';

afterEach(() => vi.unstubAllGlobals());

describe('content boundaries', () => {
  it('escapes model HTML instead of executing it as Markdown', () => {
    const html = renderToStaticMarkup(<RichText text={'<script>alert(1)</script>\n**Advice** [S2]'}/>);
    expect(html).not.toContain('<script>');
    expect(html).toContain('&lt;script&gt;');
    expect(html).toContain('<strong>Advice</strong>');
    expect(html).toContain('S2</sup>');
  });
  it('keeps artifacts inside an opaque sandbox with no privileges', () => {
    const html = renderToStaticMarkup(<ArtifactPreview title="Brief" html="<h1>Plan</h1>"/>);
    expect(html).toContain('sandbox=""');
    expect(html).toContain('referrerPolicy="no-referrer"');
    expect(html).not.toContain('allow-scripts');
    expect(html).not.toContain('allow-same-origin');
  });
  it('only links credential-free HTTPS evidence sources', () => {
    expect(sourceUrl('javascript:alert(1)')).toBeUndefined();
    expect(sourceUrl('https://user:secret@example.com')).toBeUndefined();
    expect(sourceUrl('http://example.com')).toBeUndefined();
    expect(sourceUrl('https://example.com/episode')).toBe('https://example.com/episode');
  });
  it('groups bullets and preserves code as inert text', () => {
    const html = renderToStaticMarkup(<RichText text={'- One\n- Two\n```html\n<img onerror="bad()">\n```'}/>);
    expect(html).toContain('<ul><li>One</li><li>Two</li></ul>');
    expect(html).not.toContain('<img');
    expect(html).toContain('&lt;img');
  });
});

describe('API errors', () => {
  it('preserves a useful message and short diagnostic reference', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ok: false, json: async () => ({
      message: 'Model timed out', request_id: '12345678-1234-1234-1234-123456789012',
    })}));
    await expect(api('/api/test')).rejects.toThrow('Model timed out · Ref 12345678');
  });
});
