# Troubleshooting

| Symptom | Check |
| --- | --- |
| Waiting | Open and authenticate the intended app as the active tab of its dedicated window. An SSO/login page, documentation page or custom title will not match. The router never signs in for you. |
| Choose | More than one matching window exists. Select the desired window and Bind, or close extra matching windows. Exact window identity is retained only until that window/process changes. |
| Codex missing | The preview requires the Store-packaged Codex identity, not just an executable named `chatgpt.exe` or a window titled Codex. Unpackaged/renamed builds need a reviewed identity update. |
| Window focused but actions refused | Press its selector again after replacement/reconnection. Release held Ctrl/Alt/Shift/Windows keys. Keep router and target at the same ordinary privilege level. |
| Browser active tab changed | Return to the app tab and press its selector. A later action rechecks title and process before dispatch. Titles can be spoofed; use trusted pages only. |
| F-key already in use | Close the other router/remapper instance. Seven F-keys are global while this router runs. Tests stub registration and can run alongside it. |
| Dictate unavailable | Configure the client's microphone and speech service; allow permission in the browser. For Hermes use dictation mode. For Pi verify server-side `PI_WEB_STT_URL`, WAV multipart support and a selected chat/project. |
| Send/New ignored during dictation | Finish recording with Dictate and wait for transcription to complete. Inspect the client error/status message before retrying. Stop is the agent-run control. |
| Startup points elsewhere | Disable startup in the old installation before migrating. The new copy refuses to replace/delete its entry. Moving an installation requires opting out before moving and opting in afterward. |
| No background window | Launch `python router.py` in a console. Check Python/Tk, a short stable path, another instance and hotkey collisions. Startup failure uses a Windows dialog; missing Python cannot execute that handler. |
| Invalid/unwritable settings | The router shows a status error. Close it, back up/remove only `%LOCALAPPDATA%\UniversalMicro\bindings.json`, then choose windows again. Do not reset Input or delete native layers. |
| Patch source checksum mismatch | Use the exact manifest commit with LF line endings in a fresh dedicated clone. Do not apply to a modified fork/deployment or bypass hashes. |

Browser discovery uses Chrome/Edge process names and titles: `Hermes` or a title ending ` — Hermes`; `Pi Web` or a title ending ` - Pi Web`, with standard Chrome/Edge suffixes removed. A window with another tab active is not eligible. Bound browsers can reconnect only within the saved browser preference; choose and Bind a different browser explicitly to change it.

The router's status line reports errors and selected actions; browser failures use a short accessible status notice. No telemetry or diagnostic log is written. If reporting a problem, give versions and synthetic reproduction steps, not window titles, chat text, recordings, account pages, full device exports or configuration files.
