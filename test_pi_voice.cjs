// Exercises the actual patched speech route and WAV encoder; no microphone or network.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {stripTypeScriptTypes} = require('node:module');
const assert = require('node:assert/strict');
const root = process.argv[2] || '.cache/pi';
function source(file) {
  return stripTypeScriptTypes(fs.readFileSync(path.join(root, file), 'utf8'))
    .replace(/^import .*;\s*$/gm, '').replace(/\bexport /g, '');
}
(async () => {
  if (!process.argv.includes('--hook-only')) {
  const env = {};
  let upstream, requests = [];
  const context = vm.createContext({Response, Request, FormData, Blob, AbortSignal,
    NextResponse: {json: (body, init) => Response.json(body, init)}, process: {env},
    fetch: async (url, options) => { requests.push({url, options}); return upstream(); }});
  vm.runInContext(source('app/api/stt/route.ts') + ';globalThis.api={GET,POST};', context);
  const post = (body = 'wav', headers = {'content-type': 'audio/wav'}) =>
    context.api.POST(new Request('https://pi.example/api/stt', {method: 'POST', body, headers}));
  assert.deepEqual(await (await context.api.GET()).json(), {enabled: false});
  assert.equal((await post()).status, 501);
  env.PI_WEB_STT_URL = 'https://speech.example';
  assert.equal((await post('')).status, 400);
  assert.equal((await post('wav', {'content-length': String(26 * 1024 * 1024)})).status, 413);
  assert.equal((await post('wav', {'content-type': 'text/plain'})).status, 415);
  let cancelled = false;
  const reader = {read: async () => ({done: false, value: new Uint8Array(26 * 1024 * 1024)}),
    cancel: async () => { cancelled = true; }};
  let response = await context.api.POST({headers: new Headers({'transfer-encoding': 'chunked'}), body: {getReader: () => reader}});
  assert.equal(response.status, 413);
  assert.equal(cancelled, true);
  upstream = () => Response.json({text: 'hardware test'});
  response = await post();
  assert.deepEqual(await response.json(), {text: 'hardware test'});
  assert.equal(requests.at(-1).url, 'https://speech.example/v1/audio/transcriptions');
  assert.equal(requests.at(-1).options.body.get('file').type, 'audio/wav');
  upstream = () => new Response('private upstream details', {status: 500});
  response = await post();
  assert.equal(response.status, 502);
  assert.ok(!(await response.text()).includes('private upstream'));
  upstream = () => { throw new Error('private upstream details'); };
  response = await post();
  assert.equal(response.status, 502);
  assert.ok(!(await response.text()).includes('private upstream'));
  upstream = () => Response.json({unexpected: true});
  assert.equal((await post()).status, 502);
  const wav = vm.createContext({Blob});
  vm.runInContext(source('lib/audio-wav.ts') + ';globalThis.audio={encodeWavBlob,audioBufferToMonoSamples};', wav);
  const samples = wav.audio.audioBufferToMonoSamples({numberOfChannels: 2,
    getChannelData: i => new Float32Array(i ? [-1, 0.5, 1] : [-1, -0.5, 1])});
  assert.deepEqual(Array.from(samples), [-1, 0, 1]);
  const data = new DataView(await wav.audio.encodeWavBlob(samples, 16000).arrayBuffer());
  assert.equal(data.byteLength, 50);
  assert.equal(data.getUint32(24, true), 16000);
  assert.deepEqual([44, 46, 48].map(i => data.getInt16(i, true)), [-32768, 0, 32767]);
  console.log('Pi speech: configuration, size/type limits, sanitized failures, transcript and WAV encoding passed.');
  }
  // Native React/browser boundaries are simulated; the actual hook owns recovery/timers.
  const cells = [], timers = new Map(), transcripts = [];
  let cursor, effects, api, clock = 0, timerId = 0, failure = 'permission denied';
  const useState = initial => {
    const index = cursor++;
    cells[index] ??= {value: typeof initial === 'function' ? initial() : initial};
    return [cells[index].value, next => { cells[index].value = typeof next === 'function' ? next(cells[index].value) : next; }];
  };
  const useRef = value => cells[cursor++] ??= {current: value};
  const useEffect = (effect, dependencies) => {
    const index = cursor++, previous = cells[index];
    if (!previous || dependencies.some((value, i) => !Object.is(value, previous[i]))) effects.push(effect);
    cells[index] = dependencies;
  };
  class Recorder {
    static isTypeSupported() { return true; }
    constructor(stream, options) { this.stream = stream; this.mimeType = options.mimeType; this.state = 'inactive'; }
    start() { this.state = 'recording'; }
    stop() { this.state = 'inactive'; this.ondataavailable({data: new Blob([new Uint8Array(1024)])}); this.onstop(); }
  }
  const hook = vm.createContext({Blob, Error, MediaRecorder: Recorder, useState, useRef, useEffect,
    useCallback: fn => { cursor++; return fn; }, blobToWav16kMono: async value => value,
    Date: class extends Date { static now() { return clock; } },
    navigator: {mediaDevices: {getUserMedia: async () => { if (failure) throw new Error(failure); return {getTracks: () => [{stop() {}}]}; }}},
    fetch: async () => Response.json({text: 'recovered dictation'}),
    window: {setTimeout: (fn, delay) => { const id = ++timerId; timers.set(id, {fn, at: clock + delay}); return id; },
      clearTimeout: id => timers.delete(id)},
  });
  vm.runInContext(source('hooks/useVoiceInput.ts') + ';globalThis.useVoice=useVoiceInput;', hook);
  const onTranscript = text => transcripts.push(text);
  const render = () => { cursor = 0; effects = []; api = hook.useVoice(onTranscript); effects.forEach(fn => fn()); };
  const advance = milliseconds => {
    clock += milliseconds;
    for (const [id, timer] of [...timers]) if (timer.at <= clock) { timers.delete(id); timer.fn(); }
    render();
  };
  render();
  await api.start(); render();
  assert.equal(api.error, 'permission denied');
  advance(6000);
  assert.equal(api.state, 'idle');
  assert.equal(api.error, null, 'Expired error must clear its banner');
  await api.start(); render();
  advance(1000);
  failure = 'newer error';
  await api.start(); render();
  advance(5000);
  assert.equal(api.error, 'newer error', 'An older timer must not clear a newer error');
  advance(1000);
  assert.equal(api.error, null);
  await api.start(); render();
  failure = null;
  const retry = api.start(); render();
  assert.equal(api.error, null, 'A new attempt must clear the previous banner immediately');
  await retry; render();
  assert.equal(api.state, 'recording');
  advance(500);
  api.stop();
  await new Promise(setImmediate);
  render();
  assert.equal(api.state, 'idle');
  assert.equal(api.error, null);
  assert.deepEqual(transcripts, ['recovered dictation']);
  console.log('Pi dictation: banner expiry, retry recovery and stale-timer ownership passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
