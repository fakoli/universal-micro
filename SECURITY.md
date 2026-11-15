# Security and privacy

GitHub private vulnerability reporting is enabled for `fakoli/universal-micro`. Use [Report a vulnerability](https://github.com/fakoli/universal-micro/security/advisories/new) to contact the maintainer privately. Do not put vulnerabilities, secrets or personal data in public issues. If GitHub's private reporting form is unavailable, keep sensitive details private until the channel is available again.

The first preview is the only planned supported version. No security audit or response-time guarantee is claimed. A report should identify the project version/adapter commit, synthetic reproduction and impact; omit recordings, chats, credentials, device exports and private deployment/model information.

## Local keyboard automation

The router registers seven global F-keys and injects the corresponding native shortcut only after explicit harness selection, current foreground/process-lifetime validation and held-modifier checks. Codex also requires the known Windows package family. Browser routing relies on an allowed executable name and a matching active-window title. A malicious local application or trusted page can spoof names/titles or generate keyboard events. This is a convenience controller, not an isolation boundary. A focus change can still race Windows input dispatch after the last check. Use it only with trusted applications/pages at the same privilege level; do not run it elevated.

No network listener, browser debugging connection, extension, telemetry, audio recorder or chat-text logging is added by the router. It reads window titles locally for discovery and display. Preferences contain only harness/browser executable choices under `%LOCALAPPDATA%\UniversalMicro`; no handles, titles, tokens or chat contents are retained. Startup is an opt-in per-user Run value with absolute interpreter/source paths. A different installation's entry is refused, not overwritten/deleted.

Browser patches run in the app's origin and share its authority. Hermes retains its existing speech path. The Pi prerequisite records audio in the browser, converts it to bounded WAV, POSTs to Pi's `/api/stt`, then forwards it to the administrator's configured speech service. It does not add service authentication. Keep Pi's existing web authentication/proxy protection enabled and the speech endpoint private or otherwise access-controlled. The route limits body size and upstream duration and avoids returning/logging upstream error bodies. Normal app speech/transcript behavior and provider retention remain outside Universal Micro's control.

The source manifest, checksums and patch validation detect accidental source drift; they do not establish upstream trust or stop someone who can edit your installed files. Review dependencies and patched code before building. Client lifecycle permission/recording checks have mocks; real devices and browser behavior still require manual acceptance.
