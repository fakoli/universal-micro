/* Reuses the maintained WebUI's public composer, recording and cancellation paths. */
window.AnvilMicro.install('hermes', () => {
  const composer = document.getElementById('msg');
  if (!composer || !composer.getClientRects().length) return null;
  const mic = document.getElementById('btnMic');
  const newChat = document.getElementById('btnNewChat');
  return {
    recording: Boolean(window._microDictationBusy?.() || window._micActive || mic?.disabled),
    dictate: mic && !mic.disabled && mic.getClientRects().length && typeof window._toggleMicCapture === 'function'
      ? () => {
        // Raw audio can auto-send; controller recording must remain dictation-only.
        if (window._microDictationMode?.() !== true) {
          if (typeof showToast === 'function') showToast('Choose dictation mode before using the Micro recorder.', 3500);
          return;
        }
        composer.focus();
        return window._toggleMicCapture();
      } : undefined,
    send: composer.value.trim() && typeof send === 'function' ? () => send() : undefined,
    stop: typeof cancelStream === 'function' ? () => cancelStream('micro-controller') : undefined,
    new: newChat && !newChat.disabled ? () => newChat.click() : undefined,
  };
});
