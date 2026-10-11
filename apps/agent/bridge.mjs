import { mkdtemp, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import {
  createAgentSession, createExtensionRuntime, ModelRuntime, SessionManager, SettingsManager,
} from '@earendil-works/pi-coding-agent';

// No discovered project instructions, plugins, shell tools, or persisted credential store.
let input = '';
for await (const chunk of process.stdin) input += chunk;
const request = JSON.parse(input);
const directory = await mkdtemp(join(tmpdir(), 'lenny-agent-'));
let session;
try {
  const local = request.provider === 'ollama';
  await writeFile(join(directory, 'models.json'), JSON.stringify({providers: {
    [request.provider]: {
      baseUrl: local ? request.baseUrl : 'https://api.anthropic.com',
      api: local ? 'openai-completions' : 'anthropic-messages',
      models: [{id: request.model, contextWindow: local ? 12288 : 200000,
        maxTokens: request.maxTokens || 900, samplingParams: {temperature: 0.2},
        ...(local ? {compat: {maxTokensField: 'max_tokens', supportsStore: false,
          supportsDeveloperRole: false, supportsReasoningEffort: false}} : {})}],
    },
  }}));
  const runtime = await ModelRuntime.create({
    authPath: join(directory, 'auth.json'), modelsPath: join(directory, 'models.json'),
  });
  await runtime.setRuntimeApiKey(request.provider, request.apiKey);
  const model = runtime.getModel(request.provider, request.model);
  if (!model) throw new Error('Model is not configured');
  const resourceLoader = {
    getExtensions: () => ({extensions: [], errors: [], runtime: createExtensionRuntime()}),
    getSkills: () => ({skills: [], diagnostics: []}),
    getPrompts: () => ({prompts: [], diagnostics: []}),
    getThemes: () => ({themes: [], diagnostics: []}),
    getAgentsFiles: () => ({agentsFiles: []}),
    getSystemPrompt: () => request.system,
    getSystemPromptSource: () => undefined,
    getAppendSystemPrompt: () => [], getAppendSystemPromptSources: () => [],
    extendResources: () => {}, reload: async () => {},
  };
  ({session} = await createAgentSession({
    cwd: directory, agentDir: directory, model, modelRuntime: runtime,
    thinkingLevel: 'off', noTools: 'all', tools: [], resourceLoader,
    sessionManager: SessionManager.inMemory(directory),
    settingsManager: SettingsManager.inMemory({
      compaction: {enabled: false}, retry: {enabled: false},
    }),
  }));
  if (session.getActiveToolNames().length) throw new Error('Unexpected active tools');
  const sections = [];
  const turns = request.essay ? 6 : 1;
  for (let i = 0; i < turns; i++) {
    const written = sections.join(' ').trim().split(/\s+/).filter(Boolean).length;
    const target = Math.max(90, Math.min(350, Math.round((1250 - written) / (turns - i))));
    const task = i === 0
      ? 'Write the headline, hook and first substantive section. Do not conclude yet.'
      : i === turns - 1
        ? 'Write the final section with a concrete proposed exercise and a decisive takeaway.'
        : 'Write the next section with a descriptive Markdown heading and a distinct argument. Do not conclude yet.';
    const prompt = request.essay
      ? (i === 0 ? request.prompt + '\n\n' : '') +
        `SECTION ${i + 1} OF 6: ${task} Write about ${target} words for THIS section. ` +
        'Use only the transcript evidence already supplied, with explicit [S1] style citations. ' +
        'Do not repeat previous paragraphs, introduce unsupported facts, or transfer advice between guests. ' +
        'Label proposed applications as suggestions. Return only this section, no commentary.'
      : request.prompt;
    await session.prompt(prompt);
    const last = session.messages.at(-1);
    if (last?.stopReason === 'error' || last?.stopReason === 'aborted') throw new Error('Model failed');
    const text = session.getLastAssistantText();
    if (text?.includes('INSUFFICIENT_EVIDENCE')) {
      sections.splice(0, sections.length, 'INSUFFICIENT_EVIDENCE');
      break;
    }
    sections.push(text);
  }
  process.stdout.write(JSON.stringify({text: sections.join('\n\n')}));
} catch {
  process.stdout.write(JSON.stringify({error: 'GENERATION_FAILED'}));
  process.exitCode = 1;
} finally {
  session?.dispose();
  await rm(directory, {recursive: true, force: true});
}
