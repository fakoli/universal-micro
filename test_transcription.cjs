// Check the real staged Hermes transcription function while its fetch is pending.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');

(async () => {
  const boot = fs.readFileSync(require('node:path').join(process.argv[2] || '.cache/hermes', 'static/boot.js'), 'utf8');
  const start = boot.indexOf('  async function _transcribeBlob(');
  const end = boot.indexOf('  function _stopTracks', start);
  assert.ok(start >= 0 && end > start);
  let complete;
  const context = vm.createContext({
    FormData, File,
    fetch: () => new Promise(resolve => { complete = resolve; }),
    setComposerStatus() {}, _commitTranscript() {},
    _isServerSttUnavailable: () => false, _allowBrowserSttFallback: () => false,
    showToast() {}, t: x => x, window: {},
  });
  vm.runInContext('let _microTranscribing=0;' + boot.slice(start, end) +
    ';globalThis.transcribe=_transcribeBlob; globalThis.busy=()=>_microTranscribing;', context);
  for (const ok of [true, false]) {
    const pending = context.transcribe(new Blob(['test'], {type:'audio/webm'}), 'draft');
    assert.equal(context.busy(), 1);
    complete({ok, status: ok ? 200 : 400, json: async () => ({transcript:'test'})});
    await pending;
    assert.equal(context.busy(), 0);
  }
  console.log('Hermes transcription: busy state covers pending fetch and clears after success/error.');
})().catch(error => { console.error(error); process.exitCode = 1; });
