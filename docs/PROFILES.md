# Apps, windows and shortcuts

Use **Apps & shortcuts** in the Windows router. Changes stay in the editor until **Apply and close**. Routing pauses while the editor is open. Applying validates all profiles, replaces global input keys and saves atomically. A collision or save failure keeps the previous configuration; if Windows also prevents restoring previous keys, routing pauses with an error until corrected. Selection clears after a successful apply.

## App profiles

- **Add app** creates a profile. Pick a running window and click **Use selected window** to fill executable, package identity and an exact title rule. Review these values before saving. Titles that change with a document/chat need a stable `contains` or `suffix` pattern instead.
- **Duplicate window** copies an app's shortcuts into a new profile. Choose a distinct title pattern and selector. Only one profile can bind a particular window; use separate windows for separate profiles.
- **Edit** changes the profile. **Remove** removes it from the router. Neither changes the app or Input's device layout.
- **Selector input key** focuses this profile. Leave it blank to use its **Focus** button. **Bind** chooses a window when several match. Binding a particular window is temporary; distinct title rules allow automatic reconnection after relaunch.

Executable names are literal lowercase basenames, such as `claude.exe`, separated by commas. An optional package family restricts matching further. The default Codex profile retains its verified package requirement. Title rules are case-insensitive and literal, with standard Chrome/Edge suffixes removed from titles and patterns:

| Rule | Meaning |
| --- | --- |
| `any` | Any title from the allowed executable/package |
| `app` | Exact app name or title ending ` — App` or ` - App` |
| `exact` | Entire title equals the pattern |
| `contains` | Pattern occurs anywhere in the title |
| `suffix` | Title ends with the pattern |

Titles and executable names can be spoofed. Only configure trusted applications/pages. The router cannot identify which composer/control has focus inside an app; its shortcuts behave as if typed on the keyboard. App dialogs and changed shortcuts still require care.

## Actions and keys

In **Action input keys**, change an action's F-key or add a lowercase action ID, such as `steer`. Edit each app to set the corresponding native shortcut. Blank input keys disable global registration; blank app shortcuts disable that app's action. Removing an action removes its per-app shortcuts.

Input keys are **F13–F24**. The twelve keys are shared by selectors and actions; duplicates are refused. Up to 32 profiles and 12 actions are supported. There is no script runner, command launcher or macro sequencing.

Output shortcuts accept one letter, digit, F1–F24 or named key, optionally preceded by `CTRL`, `ALT`, `SHIFT` and/or `WIN`. Examples: `CTRL+SHIFT+D`, `ENTER`, `ALT+LEFT`, `CTRL+ENTER`. Named keys include `ESC`, `TAB`, `SPACE`, `BACKSPACE`, `DELETE`, `INSERT`, `HOME`, `END`, `PAGEUP`, `PAGEDOWN`, arrow names, `PLUS` and `MINUS`. An unmodified output key cannot also be a registered input key, to prevent feedback loops. Shortcuts use native virtual keys and may vary with keyboard layout or app settings.

These changes do not reprogram the pad. In Input, assign each F-key to an unused button in your **Universal Micro** layer. Export a full layout backup first and preserve all native layers. Upgrading an existing seven-key setup only needs **F16** on the previously unassigned second key of the second row for Claude; the other assignments stay the same.

Claude defaults: **Ctrl+D** toggles dictation, **Enter** sends, **Escape** stops, and **Ctrl+N** opens a new chat. These were checked in the Windows app's shortcut list; app updates or user settings can change them. Configure microphone access in Claude itself and finish dictation before Send. Hermes/Pi retain their patched-client controls.

## Local files and recovery

`%LOCALAPPDATA%\UniversalMicro\profiles.json` contains version 1 configuration: `hotkeys` maps action IDs to input F-keys, and `apps` maps profile IDs to names, selectors, executable/package/title rules and action shortcuts. The editor is the supported way to change it. Unknown/duplicate fields and invalid shortcuts are refused. Files larger than 64 KiB are refused.

The file can contain private window-title patterns you chose. Do not include it in issues, source commits or archives. It stores no credentials, recordings or transcripts. `bindings.json` separately stores executable preferences. A legacy adjacent `.local/bindings.json` is read only if the new bindings file does not exist.

If a profile file is invalid, startup is refused and the file is unchanged. Close the router, back up/rename only `profiles.json`, then relaunch to recover defaults. For a hotkey collision, the main window stays available: open **Apps & shortcuts** and choose a free key. Native Codex Layer 1 remains independent of this router throughout.
