/* Loaded after web-controller.js; data attributes mark the existing native buttons. */
window.AnvilMicro.install('pi', () => {
  const visible = selector => [...document.querySelectorAll(selector)].filter(element => element.getClientRects().length);
  const composers = visible('[data-micro-composer]');
  if (composers.length !== 1) return null;
  const composer = composers[0];
  const button = action => {
    const matches = visible(`[data-micro-action="${action}"]`);
    return matches.length === 1 ? matches[0] : null;
  };
  const dictate = button('dictate'), send = button('send'), stop = button('stop');
  return {
    recording: ['requesting', 'recording', 'transcribing'].includes(dictate?.getAttribute('data-micro-state')),
    dictate: dictate && !dictate.disabled ? () => { composer.focus(); dictate.click(); } : undefined,
    send: send && !send.disabled ? () => send.click() : undefined,
    stop: stop && !stop.disabled ? () => stop.click() : undefined,
    new: () => window.dispatchEvent(new KeyboardEvent('keydown', {
      key: 'n', ctrlKey: true, altKey: true, bubbles: true,
    })),
  };
});
