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
})().catch(error => { console.error(error); process.exitCode = 1; });
