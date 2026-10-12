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
  await session.prompt(request.prompt);
  const last = session.messages.at(-1);
  if (last?.stopReason === 'error' || last?.stopReason === 'aborted') throw new Error('Model failed');
  process.stdout.write(JSON.stringify({text: session.getLastAssistantText()}));
} catch {
  process.stdout.write(JSON.stringify({error: 'GENERATION_FAILED'}));
  process.exitCode = 1;
} finally {
  session?.dispose();
  await rm(directory, {recursive: true, force: true});
}
