# Manual compatibility checks

These checks extend the experimental source preview's validation. Unchecked items remain documented follow-up; the owner authorized publishing the preview with those limits.

Use a disposable chat, a harmless synthetic prompt and an exported device-layout backup. The owner should operate native Codex UI controls. Do not test against a valuable draft/run. Automated checks do not demonstrate real microphone, Input import, foreground input, accessibility or reboot behavior.

Windows restart/sign-in validation is owner-managed follow-up in a separate session. It is outside this workstream's completion requirements; the optional procedure below is guidance, not a blocking gate.

## Fresh Windows account or VM

- [ ] Follow only README/public-source instructions with Python/Tk and Node/Git installed. No retained source snapshots, private fork access or operator files may be required.
- [ ] Back up the full Input layout, add/import only the Universal Micro layer and confirm every pre-existing layer is unchanged. Verify the touch sensor returns to the original native Codex layer and its controls still work.
- [ ] Launch the router without elevation. Keyboard-tab through selectors/Bind/Refresh/startup controls; verify visible focus, readable status text and screen-reader names. Check display scaling and a narrow window. Record accessibility limits rather than assuming Tk labels supply every accessible association.
- [ ] Check discovery with only Codex, Hermes or Pi open, all three open, missing apps, login pages, similarly named ChatGPT/unrelated apps, changed/custom titles, inactive tabs, two matching windows and browser preference changes.
- [ ] Use F13/F14/F15/F16 to focus Codex/Hermes/Pi/Claude. After binding or a window/process replacement, require selection again. Confirm actions do not follow a stale or ambiguous target.
- [ ] In Apps & shortcuts, add a synthetic window profile and custom action, apply/reopen, then remove them. Check Cancel, duplicate/occupied input keys, disabled actions, read-only settings and overlapping window rules. Confirm the original profiles and native layers remain intact.
- [ ] On each app, F19 starts dictation; another F19 finishes and inserts a draft without sending. F20 submits it; F21 stops a sufficiently long harmless run; F22 opens a blank chat. In Pi select a project first.
- [ ] While recording or awaiting transcription, Send/New must be refused. Check denied microphone permission, missing/offline speech service, error cleanup, repeated keys, IME composition, visible dialogs and hidden/unfocused pages. Check Hermes raw-audio refusal. Stop remains the run control.
- [ ] Change foreground focus and hold Ctrl/Alt/Shift/Windows keys; verify dispatch refusal. Check a minimized or unresponsive target, target closure, same HWND/PID reused by another process lifetime and both browser windows sharing one process.
- [ ] Close/relaunch the router and each client; no manual binding should be needed when a unique eligible window exists. Open an extra matching window to confirm ambiguity requires a choice.

## Startup, upgrade and removal

- [ ] Reopen the launcher and confirm one instance. Simulate a second installation's Run value in a disposable account: neither enabling nor disabling may change its value or unrelated startup entries.
- [ ] Migrate using README's opt-out/close/launch/opt-in sequence. Move a source/interpreter path only after disabling startup; confirm re-enabling points to the new location.
- [ ] Disable startup, close and remove this installation and its optional preferences/layer. Confirm unrelated startup entries, original Input layers and native Codex fallback still work.
- [ ] Verify client source patch reversal and deployed-release rollback separately; no source-tool action may restart a service automatically.

## Optional owner restart check in a separate session

With startup enabled, restart or sign out/in and confirm one minimized router appears and reconnects; the first action still needs a selector. If separately checking removal, confirm a disabled/removed installation stays removed after sign-in. Leave unrelated startup entries and native Input layers intact. These checks are not required to complete this workstream.

Record versions, public adapter commits, date, pass/fail and synthetic reproduction for failures. Do not collect private chats, recordings, account pages, full device exports or deployment/model metadata in the public evidence. A second person can use the reviewed archive to qualify broader compatibility claims; the optional owner restart check is separate.
