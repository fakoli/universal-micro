/* Shared keyboard contract; adapters resolve current native controls on every press. */
(() => {
  const bindings = {
    hermes: {d: 'dictate', enter: 'send', x: 'stop', n: 'new'},
    pi: {r: 'dictate', s: 'send', t: 'stop', c: 'new'},
  };
  window.AnvilMicro = {
    install(harness, resolve, notice = text => {
      let output = document.getElementById('anvil-micro-status');
      if (!output) {
        output = document.createElement('output');
        output.id = 'anvil-micro-status';
        output.setAttribute('role', 'status');
        output.style.cssText = 'position:fixed;bottom:16px;left:16px;z-index:2147483647;background:#222;color:white;padding:10px 14px;border-radius:8px;font:14px system-ui;max-width:420px;pointer-events:none';
        document.body.append(output);
      }
      output.textContent = text;
      clearTimeout(output.microTimer);
      output.microTimer = setTimeout(() => output.remove(), 3500);
    }) {
      const keys = bindings[harness];
      if (!keys) throw new Error('Unknown controller harness');
      const pending = new Set();
      window.addEventListener('keydown', async event => {
        if (!event.ctrlKey || !event.altKey || !event.shiftKey || event.metaKey) return;
        const action = keys[String(event.key).toLowerCase()];
        if (!action || event.repeat || event.isComposing || event.keyCode === 229) return;
        const doc = window.document;
        if (doc.hidden || !doc.hasFocus()) return;
        event.preventDefault();
        event.stopPropagation();
        const dialogs = doc.querySelectorAll('[aria-modal="true"],dialog[open],.modal.open,.modal-overlay.open');
        if ([...dialogs].some(element => element.getClientRects().length)) return;
        const controls = resolve();
        if (!controls) return notice('Open a chat composer first.');
        if ((controls.recording || pending.has('dictate')) && (action === 'send' || action === 'new')) {
          return notice('Finish dictation before sending or opening a new chat.');
        }
        if (pending.has(action)) return;
        if (typeof controls[action] !== 'function') return notice('That action is not available right now.');
        pending.add(action);
        try {
          await controls[action]();
        } catch {
          notice('The app could not complete that action.');
        } finally {
          pending.delete(action);
        }
      }, true);
    },
  };
})();
