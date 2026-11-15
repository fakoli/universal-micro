# Pinned browser integrations

Use a **dedicated source checkout**, separate from any deployed client. These commands obtain only public sources, verify their immutable revision and touched-file SHA-256 values, and apply the reviewed ordered patch series in [adapters.json](../adapters.json). No router command deploys files or restarts a service. Source builds require each client's own dependencies and setup.

Run commands from Universal Micro's folder. Git's LF settings are required on Windows; changed bytes, repeat application, dirty checkouts, wrong revisions and changed patch hashes are refused.

## Hermes WebUI

```powershell
git clone -c core.autocrlf=false -c core.eol=lf --no-checkout https://github.com/fakoli/hermes-webui.git .cache/hermes
git -C .cache/hermes checkout --detach 4772f16a95b5b7ad641780b6bd8a6a38f2109fb3
python prepare_integrations.py hermes .cache/hermes --mode check
python prepare_integrations.py hermes .cache/hermes --mode apply
node test_transcription.cjs .cache/hermes
node --check .cache/hermes/static/boot.js
```

The patch adds the shared dispatcher and Hermes adapter to `static/`, loads them after `boot.js`, and exposes dictation mode/busy state through the existing recording/transcription lifecycle. Send and New chat wait for recording/transcription to finish. Active raw capture is refused even if its preference has changed; capture mode is pinned before waiting for microphone permission. Existing Send, Stop, New and microphone code remains authoritative; no server or stream registry is added.

Follow the pinned client's own installation/security instructions to deploy your reviewed source. For this static-only adapter, browser refresh is required; a Hermes server restart is not required by the patch. Authenticate, open a chat and configure a working native microphone/dictation path before testing the pad.

## Pi Web

```powershell
git clone -c core.autocrlf=false -c core.eol=lf --no-checkout https://github.com/agegr/pi-web.git .cache/pi
git -C .cache/pi checkout --detach 174bff967807cdb59abb0204198d3d7cc19c862d
python prepare_integrations.py pi .cache/pi --mode check
python prepare_integrations.py pi .cache/pi --mode apply
node test_pi_voice.cjs .cache/pi
```

Patch order is `pi-01-dictation.patch` then `pi-02-controller.patch`:

1. Adds an owned, generic React dictation hook, WAV encoder, `/api/stt` route and composer microphone control. The hook records at most five minutes, converts to mono PCM16 WAV at 16 kHz and inserts the returned text as a draft. The speech route bounds streamed bodies to 25 MiB, times out the upstream request after 120 seconds and returns concise errors without upstream bodies or endpoint details.
2. Marks existing composer/send/stop controls and loads the shared dispatcher and Pi adapter. New chat invokes Pi's existing Ctrl+Alt+N shortcut; a project must already be selected. Multiple visible composers are refused.

Configure **`PI_WEB_STT_URL` on the Pi server**, never as a public browser environment variable. It may be a speech-service base URL or its complete `/v1/audio/transcriptions` endpoint. For example, `https://speech.example/v1/audio/transcriptions` is a placeholder; replace it with your own service. The required API accepts multipart `file` and returns JSON `{ "text": "recognized words" }`. This preview does not implement speech-service authentication or choose a speech model. Use a suitably protected endpoint reachable by the Pi server.

The browser needs HTTPS or a browser-trusted local origin and microphone permission. Audio goes to your Pi server, then the configured speech endpoint. The router never receives it. Pi's authentication, access policy and reverse proxy remain your responsibility; do not expose a development instance or an unauthenticated transcription endpoint to the Internet.

For an isolated build check, without running install hooks or a server:

```powershell
Push-Location .cache/pi
npm ci --ignore-scripts --no-audit --no-fund
$env:NEXT_TELEMETRY_DISABLED = '1'
npm run build
node --experimental-strip-types --test components/ChatInput.test.mjs components/ChatInput.focus.test.mjs components/ChatInput.dormancy.test.mjs hooks/useKeyboardShortcuts.test.mjs
Pop-Location
```

For actual runtime installation, follow Pi's pinned upstream guide, including its native terminal dependency preparation. Deploy into a separate release directory with the required speech configuration; Pi needs a build and service restart to load changed React/server code. Retain your prior release for rollback. These are owner-operated deployment steps, outside this preparation script.

## Reversal and upgrades

```powershell
python prepare_integrations.py hermes .cache/hermes --mode reverse
python prepare_integrations.py pi .cache/pi --mode reverse
```

Reverse checks all patched-file hashes and the reverse patch before writing. Local edits to patched files or unrelated tracked changes are refused. Do not force a rollback across your changes: keep that checkout and create another clean pinned checkout instead. To roll back a deployment, restore the prior client release and refresh Hermes, or rebuild/restart Pi as appropriate. Reversing a source checkout does not alter a running deployed release.

Upgrades require a new reviewed public base commit, updated original/patched-file and patch hashes, preserved MIT notices, apply/reverse tests, client compile checks and manual acceptance. A patch cannot be assumed compatible with a newer client because it applies. Maintain narrow patches; do not vendor complete client trees or make a private fork public to satisfy these instructions.

## Shortcut contract

| Action | Codex native | Hermes adapter | Pi adapter |
| --- | --- | --- | --- |
| Dictate | Ctrl+Shift+D | Ctrl+Alt+Shift+D | Ctrl+Alt+Shift+R |
| Send | Ctrl+Enter | Ctrl+Alt+Shift+Enter | Ctrl+Alt+Shift+S |
| Stop run | Escape | Ctrl+Alt+Shift+X | Ctrl+Alt+Shift+T |
| New chat | Ctrl+N | Ctrl+Alt+Shift+N | Ctrl+Alt+Shift+C |

The browser controller ignores repeats, IME composition, Meta-modified chords, hidden/unfocused pages and visible modal dialogs. Shortcuts are scoped per adapter. They are ordinary keyboard events, not a remote-control API or an authentication boundary.
