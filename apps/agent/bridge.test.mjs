import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';

for (const maxTokens of [123, 3000]) {
test(`Pi sends bounded, tool-free requests (${maxTokens} tokens)`, async () => {
  const captured = [];
  const server = createServer(async (req, res) => {
    let body = '';
    for await (const chunk of req) body += chunk;
    captured.push(JSON.parse(body));
    res.writeHead(200, {'Content-Type': 'text/event-stream'});
    for (const [delta, finish_reason] of [
      [{role: 'assistant', content: 'Supported advice [S1]'}, null], [{}, 'stop'],
    ]) {
      res.write(`data: ${JSON.stringify({id: 'test', object: 'chat.completion.chunk',
        created: 0, model: 'test-model', choices: [{index: 0, delta, finish_reason}]})}\n\n`);
    }
    res.end('data: [DONE]\n\n');
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  try {
    const child = spawn(process.execPath, [fileURLToPath(new URL('./bridge.mjs', import.meta.url))],
      {stdio: ['pipe', 'pipe', 'pipe']});
    let output = '';
    child.stdout.on('data', chunk => { output += chunk; });
    child.stdin.end(JSON.stringify({provider: 'ollama', model: 'test-model',
      baseUrl: `http://127.0.0.1:${server.address().port}/v1`, apiKey: 'ollama',
      system: 'Use only evidence. Cite [S1].', prompt: 'A test question', maxTokens}));
    const code = await new Promise(resolve => child.on('close', resolve));
    assert.equal(code, 0, output);
    const turns = 1;
    assert.equal(captured.length, turns);
    assert.deepEqual(JSON.parse(output), {text: Array(turns).fill('Supported advice [S1]').join('\n\n')});
    for (const [i, request] of captured.entries()) {
      assert.equal(request.messages[0].role, 'system');
      assert.match(request.messages[0].content, /Use only evidence/);
      assert.equal(request.max_tokens, maxTokens);
      assert.equal(request.tools, undefined);
      assert.equal(request.temperature, 0.2);
      assert.equal(request.messages.filter(m => m.role === 'assistant').length, i);
    }
  } finally {
    await new Promise(resolve => server.close(resolve));
  }
});
}
