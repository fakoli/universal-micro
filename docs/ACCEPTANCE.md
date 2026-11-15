# Manual acceptance before a public preview

Use a disposable chat, a harmless synthetic prompt and an exported device-layout backup. The owner should operate native Codex UI controls. Do not test against a valuable draft/run. Automated checks do not demonstrate real microphone, Input import, foreground input, accessibility or reboot behavior.

## Fresh Windows account or VM

- [ ] Follow only README/public-source instructions with Python/Tk and Node/Git installed. No retained source snapshots, private fork access or operator files may be required.
- [ ] Back up the full Input layout, add/import only the Universal Micro layer and confirm every pre-existing layer is unchanged. Verify the touch sensor returns to the original native Codex layer and its controls still work.
- [ ] Launch the router without elevation. Keyboard-tab through selectors/Bind/Refresh/startup controls; verify visible focus, readable status text and screen-reader names. Check display scaling and a narrow window. Record accessibility limits rather than assuming Tk labels supply every accessible association.
- [ ] Check discovery with only Codex, Hermes or Pi open, all three open, missing apps, login pages, similarly named ChatGPT/unrelated apps, changed/custom titles, inactive tabs, two matching windows and browser preference changes.
- [ ] Use F13/F14/F15 to focus the intended harness. After binding or a window/process replacement, require selection again. Confirm actions do not follow a stale or ambiguous target.
- [ ] On each app, F19 starts dictation; another F19 finishes and inserts a draft without sending. F20 submits it; F21 stops a sufficiently long harmless run; F22 opens a blank chat. In Pi select a project first.
- [ ] While recording or awaiting transcription, Send/New must be refused. Check denied microphone permission, missing/offline speech service, error cleanup, repeated keys, IME composition, visible dialogs and hidden/unfocused pages. Check Hermes raw-audio refusal. Stop remains the run control.
- [ ] Change foreground focus and hold Ctrl/Alt/Shift/Windows keys; verify dispatch refusal. Check a minimized or unresponsive target, target closure, same HWND/PID reused by another process lifetime and both browser windows sharing one process.
- [ ] Close/relaunch the router and each client; no manual binding should be needed when a unique eligible window exists. Open an extra matching window to confirm ambiguity requires a choice.

## Startup, upgrade and removal

- [ ] With startup disabled, restarting Windows does not start this router. Enable startup, then perform an actual sign-out/sign-in or reboot: one minimized router appears and reconnects; the first action still needs a selector.
- [ ] Reopen the launcher and confirm one instance. Simulate a second installation's Run value in a disposable account: neither enabling nor disabling may change its value or unrelated startup entries.
- [ ] Migrate using README's opt-out/close/launch/opt-in sequence. Move a source/interpreter path only after disabling startup; confirm re-enabling points to the new location.
- [ ] Disable startup, close and remove this installation and its optional preferences/layer. After sign-in, it stays removed; unrelated startup entries, original Input layers and native Codex fallback still work.
- [ ] Verify client source patch reversal and deployed-release rollback separately; no source-tool action may restart a service automatically.

Record versions, public adapter commits, date, pass/fail and synthetic reproduction for failures. Do not collect private chats, recordings, account pages, full device exports or deployment/model metadata in the public evidence. A second person should complete this pass from the reviewed archive before publication.
