# Apps, windows and shortcuts

Use **Apps & shortcuts** in the Windows router. Changes stay in the editor until **Apply and close**. Routing pauses while the editor is open. Applying validates all profiles, replaces global input keys and saves atomically. A collision or save failure keeps the previous configuration; if Windows also prevents restoring previous keys, routing pauses with an error until corrected. Selection clears after a successful apply.

There are two settings to connect: **Input makes the pad emit an F-key; the router decides what that F-key does.** A selector focuses an already-open app/window. An action sends that app's configured native shortcut. The router does not launch apps or add capabilities such as dictation to apps that lack them.

| Example input | Router behavior |
| --- | --- |
| F17 assigned to an app's selector | Focus that app/window |
| F20 assigned to `send` | Send the selected app's `send shortcut`, such as `ENTER` or `CTRL+ENTER` |
| F23 assigned to a new `find` action | Send the selected app's configured `find shortcut`, such as `CTRL+F` |

## Add another app

1. Open the app and leave its intended main window visible. Check its own keyboard-shortcut list for the actions you want to control.
2. In Universal Micro, click **Apps & shortcuts**, then **Add app** on **Apps and windows**.
3. In the window dropdown below **Window title pattern**, choose the desired running window and click **Use selected window**. This fills **Executable names**, **Package family**, and an `exact` title rule.
4. Set **Unique ID** to an unused lowercase ID such as `notes`, and **Display name** to the label you want in the router. You can keep the generated ID instead.
5. Choose an unused **Selector input key**, for example **F17**. Leave it blank if you prefer the router's **Focus** button.
6. Review **Window title match** and **Window title pattern**. Keep `exact` for a stable title. If the title changes with the current document/chat, use a stable `app`, `contains` or `suffix` rule from the reference below. Avoid `any` for shared browser executables: it would also match unrelated browser windows.
7. Fill the app's shortcut rows with its actual native chords. For example, use `ENTER` for `send` only if that app uses Enter to send. Leave unsupported actions blank. Existing F19/F20/F21/F22 action keys can keep their assignments; the per-app output shortcuts may differ.
8. Click **Keep changes**, then **Apply and close**. Keep changes updates the editor's draft; Apply saves and activates it.
9. Back in the main router, check the new row. One matching window connects automatically. If the row says **Choose**, select the intended window in its dropdown and click **Bind**. Click **Focus** to check that it selects the right window.
10. Assign the selector's F-key to a pad button using the Input steps below. Press the selector, then test the action buttons in a disposable chat/document.

### Assign the same F-key in Input

1. Export/back up your full device layout in Input.
2. Open **Keymap** and select your **Universal Micro** layer (usually Layer 3). Preserve the native Codex layers.
3. Click an unused button to open **Key Mapping**. Search for the chosen key, such as `F17`, in **Basic**.
4. Drag that F-key from the picker onto the unused button. Wait for **Layout updated**.
5. Select the Universal Micro layer on the physical pad and press the new selector. Then use the existing action buttons.

With the shipped defaults, F17, F18, F23 and F24 are free; selectors and actions share that pool. Choose another free key if you have already customized them. A router key change does not reprogram Input. If you only edit an app's output shortcut and keep its input F-key, no Input change is needed.

## Add a second window of the same app

1. Open both intended windows. In **Apps & shortcuts**, select the existing app and click **Edit**.
2. Narrow the original profile's title rule to its intended window, then **Keep changes**. For example, if the app exposes titles `Planning — Example App` and `Writing — Example App`, the original could use `contains` with `Planning`.
3. Select that profile and click **Duplicate window**. Give the copy a different ID/display name, a free selector such as **F18**, and a title pattern for the second window, such as `contains` with `Writing`. Its native shortcuts are copied from the original.
4. Click **Keep changes**, then **Apply and close**. Check that each row connects to its own window. Assign the new selector in Input as above.

Make the rules distinct for **both** profiles. A broad original rule can otherwise claim the new profile's window. Each controlled profile requires a separate window; profiles cannot share a bound window, and browser profiles do not switch tabs.

If the windows have identical titles and executable/package identities, title matching cannot distinguish them automatically. Open both windows, select a different window in each router row and click **Bind**. These particular window bindings last only for the current windows; repeat them after relaunch. Distinct stable title rules are what allow automatic reconnection.

## Add or change an action hotkey

1. Open **Apps & shortcuts → Action input keys**.
2. To reassign an existing action, choose its new unused F-key. To add one, click **Add action**, enter a lowercase ID such as `find`, then choose a free input key such as **F23**.
3. Return to **Apps and windows**, select the app and click **Edit**. Enter its native shortcut in the new action row: for example, `CTRL+F` in **find shortcut** if that app uses it for Find. Leave it blank in apps where the action should do nothing.
4. Click **Keep changes**, then **Apply and close**.
5. In Input, assign the same new action F-key to an unused button on the Universal Micro layer. Press the app's selector before using the action.

Action input keys are shared across apps. For example, changing `send` from F20 changes its input for every profile, while editing one app's `send shortcut` changes only that app's output. An action name labels a shortcut; it does not implement a new app feature. Cancel closes the editor without applying its draft.

## App profile reference

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

## Shortcut reference

In **Action input keys**, change an action's F-key or add a lowercase action ID, such as `steer`. Edit each app to set the corresponding native shortcut. Blank input keys disable global registration; blank app shortcuts disable that app's action. Removing an action removes its per-app shortcuts.

Input keys are **F13–F24**. The twelve keys are shared by selectors and actions; duplicates are refused. Up to 32 profiles and 12 actions are supported. There is no script runner, command launcher or macro sequencing.

Output shortcuts accept one letter, digit, F1–F24 or named key, optionally preceded by `CTRL`, `ALT`, `SHIFT` and/or `WIN`. Examples: `CTRL+SHIFT+D`, `ENTER`, `ALT+LEFT`, `CTRL+ENTER`. Named keys include `ESC`, `TAB`, `SPACE`, `BACKSPACE`, `DELETE`, `INSERT`, `HOME`, `END`, `PAGEUP`, `PAGEDOWN`, arrow names, `PLUS` and `MINUS`. An unmodified output key cannot also be a registered input key, to prevent feedback loops. Shortcuts use native virtual keys and may vary with keyboard layout or app settings.

These changes do not reprogram the pad. In Input, assign each F-key to an unused button in your **Universal Micro** layer. Export a full layout backup first and preserve all native layers. Upgrading an existing seven-key setup only needs **F16** on the previously unassigned second key of the second row for Claude; the other assignments stay the same.

Claude defaults: **Ctrl+D** toggles dictation, **Enter** sends, **Escape** stops, and **Ctrl+N** opens a new chat. These were checked in the Windows app's shortcut list; app updates or user settings can change them. Configure microphone access in Claude itself and finish dictation before Send. Hermes/Pi retain their patched-client controls.

## Local files and recovery

`%LOCALAPPDATA%\UniversalMicro\profiles.json` contains version 1 configuration: `hotkeys` maps action IDs to input F-keys, and `apps` maps profile IDs to names, selectors, executable/package/title rules and action shortcuts. The editor is the supported way to change it. Unknown/duplicate fields and invalid shortcuts are refused. Files larger than 64 KiB are refused.

The file can contain private window-title patterns you chose. Do not include it in issues, source commits or archives. It stores no credentials, recordings or transcripts. `bindings.json` separately stores executable preferences. A legacy adjacent `.local/bindings.json` is read only if the new bindings file does not exist.

If a profile file is invalid, startup is refused and the file is unchanged. Close the router, back up/rename only `profiles.json`, then relaunch to recover defaults. For a hotkey collision, the main window stays available: open **Apps & shortcuts** and choose a free key. Native Codex Layer 1 remains independent of this router throughout.
