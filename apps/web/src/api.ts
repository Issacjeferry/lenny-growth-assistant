export type Evidence = { id: string; title: string; guest: string; url: string; excerpt: string; timestamp_seconds: number | null; distance: number; label?: string };
export type Message = { id: string; role: string; content: string; citations: Evidence[]; provider: string | null; model: string | null; status: string; created_at: string };
export type Artifact = { id: string; message_id: string; title: string; type: string; content: string };
export type Session = { id: string; title: string; created_at: string };
export type Detail = Session & { messages: Message[]; artifacts: Artifact[] };
export type Mode = 'qa' | 'ship30' | 'html' | 'markdown';

export async function api<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(path, body === undefined ? undefined : {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(`${data.message || 'Request failed'}${data.request_id ? ` · Ref ${data.request_id.slice(0, 8)}` : ''}`);
  return data as T;
}

export function sourceUrl(value: string): string | undefined {
  try { const url = new URL(value); return url.protocol === 'https:' && !url.username && !url.password ? url.href : undefined; }
  catch { return undefined; }
}
