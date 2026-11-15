// Run: node test_web_controller.cjs
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

(async () => {
  const calls = [], notices = [];
  let handler, focused = true, modal = false, recording = false;
  const doc = {
    hidden: false,
    hasFocus: () => focused,
    querySelectorAll: () => modal ? [{getClientRects: () => [1]}] : [],
  };
  const win = {document: doc, addEventListener: (_, fn) => { handler = fn; }};
  vm.runInNewContext(fs.readFileSync('web-controller.js', 'utf8'), {window: win});
  const controls = Object.fromEntries(['dictate', 'send', 'stop', 'new'].map(action => [action, () => calls.push(action)]));
  win.AnvilMicro.install('hermes', () => ({...controls, recording}), text => notices.push(text));
  async function press(key, extras = {}) {
    const event = {key, ctrlKey: true, altKey: true, shiftKey: true, metaKey: false,
      repeat: false, isComposing: false, preventDefault() {}, stopPropagation() {}, ...extras};
    await handler(event);
  }
  for (const key of ['d', 'Enter', 'x', 'n']) await press(key);
  assert.deepEqual(calls, ['dictate', 'send', 'stop', 'new']);
  calls.length = 0;
  for (const key of ['r', 's', 't', 'c']) await press(key); // Pi-scoped chords cannot reach Hermes.
  assert.deepEqual(calls, []);
  for (const extras of [{repeat:true}, {isComposing:true}, {keyCode:229}, {metaKey:true}, {altKey:false}]) await press('Enter', extras);
  focused = false; await press('Enter'); focused = true;
  doc.hidden = true; await press('Enter'); doc.hidden = false;
  modal = true; await press('Enter'); modal = false;
  assert.deepEqual(calls, []);
  recording = true;
  await press('Enter'); await press('n'); await press('x');
  assert.deepEqual(calls, ['stop']);
  recording = false;
  controls.send = undefined;
  await press('Enter');
  assert.deepEqual(calls, ['stop']);
  assert.ok(notices.length >= 3);
  let finish;
  controls.new = () => new Promise(resolve => { finish = resolve; calls.push('new'); });
  const pending = press('n');
  await press('n');
  assert.equal(calls.filter(x => x === 'new').length, 1);
  finish(); await pending;
  controls.stop = () => { throw new Error('test native failure'); };
  await press('x');
  assert.equal(notices.at(-1), 'The app could not complete that action.');
  let resolveHermes, raw = false, recordings = 0;
  const nativeNotices = [];
  const composer = {value:'', focus() {}, getClientRects: () => [1]};
  const mic = {disabled:false, getClientRects: () => [1]};
  const hermesWindow = {
    AnvilMicro: {install: (name, resolve) => { assert.equal(name, 'hermes'); resolveHermes = resolve; }},
    _microDictationMode: () => !raw,
    _toggleMicCapture: () => { recordings++; },
  };
  vm.runInNewContext(fs.readFileSync('integrations/hermes.js', 'utf8'), {
    window: hermesWindow,
    document: {getElementById: id => id === 'msg' ? composer : id === 'btnMic' ? mic : null},
    showToast: text => nativeNotices.push(text),
  });
  await resolveHermes().dictate();
  assert.equal(recordings, 1);
  raw = true;
  await resolveHermes().dictate();
  assert.equal(recordings, 1, 'Raw audio must not enter the native auto-send recording path');
  assert.ok(nativeNotices[0].includes('dictation'));
  let resolvePi, duplicates = false, busy = false;
  const piCalls = [];
  const piComposer = {getClientRects: () => [1], focus: () => piCalls.push('focus')};
  const piButtons = Object.fromEntries(['dictate', 'send', 'stop'].map(action => [action, {
    disabled: false, getClientRects: () => [1], click: () => piCalls.push(action),
    getAttribute: () => busy ? 'transcribing' : 'idle',
  }]));
  vm.runInNewContext(fs.readFileSync('integrations/pi.js', 'utf8'), {
    window: {AnvilMicro: {install: (_, resolve) => { resolvePi = resolve; }},
      dispatchEvent: event => { assert.equal(event.key, 'n'); assert.ok(event.ctrlKey && event.altKey); piCalls.push('new'); }},
    KeyboardEvent: class { constructor(type, options) { Object.assign(this, options); } },
    document: {querySelectorAll: selector => selector === '[data-micro-composer]' ?
      (duplicates ? [piComposer, piComposer] : [piComposer]) : [piButtons[selector.match(/="(\w+)"/)[1]]]},
  });
  for (const action of ['dictate', 'send', 'stop', 'new']) resolvePi()[action]();
  assert.deepEqual(piCalls, ['focus', 'dictate', 'send', 'stop', 'new']);
  busy = true; assert.equal(resolvePi().recording, true);
  piButtons.send.disabled = true; assert.equal(resolvePi().send, undefined);
  duplicates = true; assert.equal(resolvePi(), null);
  console.log('Web controller: both adapters, focus/modal/IME/recording/raw-audio and duplicate/error guards passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
