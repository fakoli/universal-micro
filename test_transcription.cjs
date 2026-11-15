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
  function captureHarness(raw, deferPermission = false) {
    let grant, sent = 0, transcribed = 0, resolveAdapter;
    const stream = {getTracks: () => [{stop() {}}]};
    const permission = deferPermission ? new Promise(resolve => { grant = () => resolve(stream); }) : Promise.resolve(stream);
    class Recorder {
      static isTypeSupported() { return true; }
      constructor(stream, options) { this.state = 'inactive'; this.mimeType = options.mimeType; }
      start() { this.state = 'recording'; }
      stop() { this.state = 'inactive'; this.ondataavailable({data: new Blob(['audio'])}); void this.onstop(); }
    }
    const composer = {value: '', focus() {}, getClientRects: () => [1]};
    const mic = {disabled: false, getClientRects: () => [1]};
    const win = {MediaRecorder: Recorder,
      AnvilMicro: {install: (_, resolve) => { resolveAdapter = resolve; }}};
    const sandbox = vm.createContext({Blob, File, window: win, MediaRecorder: Recorder,
      navigator: {mediaDevices: {getUserMedia: () => permission}},
      document: {getElementById: id => id === 'msg' ? composer : id === 'btnMic' ? mic : null},
      composer, S: {pendingFiles: []}, renderTray() {}, showToast() {}, t: x => x,
      send: () => { sent++; }, _transcribeBlob: async () => { transcribed++; },
      _micButtonAvailable: () => true, _micOriginNeedsSecureContext: () => false,
      _setRecording: on => { win._micActive = on; }, _stopTracks() {}, _applyDeferredServerSttFlip() {},
    });
    const extract = (first, next) => {
      const start = boot.indexOf(first), end = boot.indexOf(next, start);
      assert.ok(start >= 0 && end > start);
      return boot.slice(start, end);
    };
    const mode = boot.match(/^  window\._microDictationMode=.*$/m);
    assert.ok(mode);
    vm.runInContext(`let _rawAudioMode=${raw}, _isRecording=false, _micStartSeq=0,
      recognition=null, _forceMediaRecorder=true, _canRecordAudio=true, _micHoldActive=false,
      _activeCaptureMode=null, mediaRecorder=null, mediaStream=null, audioChunks=[], _prefix='', _finalText='';
      const ta=composer;` + mode[0] +
      extract('  function _sendRawAudio(', '  function _commitTranscript(') +
      extract('  function _stopMic(', '  function _ensureSpeechRecognition(') +
      extract('  async function _startMicCapture(', "  btn.addEventListener('pointerdown'") +
      ';globalThis.start=_startMicCapture;globalThis.setRaw=value=>{_rawAudioMode=value};globalThis.mode=()=>_activeCaptureMode;', sandbox);
    vm.runInContext(fs.readFileSync('integrations/hermes.js', 'utf8'), sandbox);
    return {start: sandbox.start, setRaw: sandbox.setRaw, mode: sandbox.mode,
      dictate: () => resolveAdapter().dictate(), nativeStop: win._stopMic, grant,
      sent: () => sent, transcribed: () => transcribed, active: () => Boolean(win._micActive)};
  }
  const raw = captureHarness(true);
  await raw.start();
  raw.setRaw(false);
  await raw.dictate();
  assert.equal(raw.sent(), 0, 'Micro must refuse an active raw recorder even after the preference changes');
  assert.equal(raw.active(), true);
  raw.nativeStop(); // Native raw stop retains its explicitly requested upstream behavior.
  assert.equal(raw.sent(), 1);
  await raw.dictate(); // A stale idle raw mode must not prevent new dictation.
  assert.equal(raw.mode(), 'media-transcribe');
  await raw.dictate();
  assert.equal(raw.sent(), 1);
  assert.equal(raw.transcribed(), 1);
  const pending = captureHarness(false, true);
  const started = pending.start();
  pending.setRaw(true);
  pending.grant();
  await started;
  assert.equal(pending.mode(), 'media-transcribe', 'Permission wait must not change dictation into raw capture');
  await pending.dictate(); // Finishing actual dictation remains safe despite the new raw preference.
  assert.equal(pending.transcribed(), 1);
  assert.equal(pending.sent(), 0);
  console.log('Hermes: pending transcription cleanup and actual capture-mode/permission-transition safety passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
