"""Universal Micro: explicit Windows targets, native app actions, no network service."""
import ctypes
from ctypes import wintypes as w
import os
import json
import queue
import subprocess
import sys
import threading
from pathlib import Path
from profiles import (DEFAULT_CONFIG, PROFILES_PATH, STATE_DIR, MODIFIERS, hotkeys,
                      key_code, load_profiles, save_profiles, shortcut_keys, validate_config)


HARNESSES = tuple(DEFAULT_CONFIG['apps'])
ACTIONS = tuple(DEFAULT_CONFIG['hotkeys'])
CODEX_KEYS = {a: shortcut_keys(k) for a, k in DEFAULT_CONFIG['apps']['codex']['shortcuts'].items()}
WEB_KEYS = {h: {a: shortcut_keys(k) for a, k in DEFAULT_CONFIG['apps'][h]['shortcuts'].items()} for h in ('hermes','pi')}
HOTKEYS = hotkeys(DEFAULT_CONFIG)
BINDINGS_PATH = STATE_DIR / 'bindings.json'
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_VALUE = "UniversalMicroRouter"


def matches_window(harness, window, config=None):
    app = (config or DEFAULT_CONFIG)['apps'].get(harness)
    if not app:
        return False
    _, process, title = window[:3]
    if process not in app['processes']:
        return False
    if app['package'] and (len(window) != 4 or window[3] != app['package']):
        return False
    caption, pattern = (s.casefold().removesuffix(" - google chrome").removesuffix(" - microsoft edge")
                        for s in (title, app['title']))
    mode = app['title_mode']
    return (mode == 'any' or mode == 'contains' and pattern in caption or
            mode == 'exact' and caption == pattern or mode == 'suffix' and caption.endswith(pattern) or
            mode == 'app' and (caption == pattern or caption.endswith(' — ' + pattern) or caption.endswith(' - ' + pattern)))


def load_bindings(path=BINDINGS_PATH, config=None):
    apps = (config or DEFAULT_CONFIG)['apps']
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    if not isinstance(data, dict) or any(h not in apps or p not in apps[h]['processes'] for h, p in data.items()):
        raise ValueError("Saved bindings are invalid; choose harness windows again")
    return data


def save_bindings(path, preferences):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(preferences, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def startup_command():
    interpreter = Path(sys.executable).with_name("pythonw.exe")
    if not interpreter.is_file():
        raise OSError("pythonw.exe is missing; repair the Python installation")
    command = subprocess.list2cmdline([str(interpreter), str(Path(__file__).resolve()), "--background"])
    if len(command) > 260:
        raise ValueError("Startup path is too long; move the router to a shorter path")
    return command


def startup_enabled():
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            value, kind = winreg.QueryValueEx(key, RUN_VALUE)
            return kind == winreg.REG_SZ and value == startup_command()
    except FileNotFoundError:
        return False


def set_startup(enabled):
    import winreg
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
        try:
            value, kind = winreg.QueryValueEx(key, RUN_VALUE)
        except FileNotFoundError:
            value, kind = None, None
        if value is not None and (kind != winreg.REG_SZ or value != startup_command()):
            raise ValueError("Startup belongs to another installation; disable it there before switching installations")
        if enabled:
            winreg.SetValueEx(key, RUN_VALUE, 0, winreg.REG_SZ, startup_command())
        else:
            try:
                winreg.DeleteValue(key, RUN_VALUE)
            except FileNotFoundError:
                pass


class Router:
    def __init__(self, desktop, preferences=None, config=None):
        self.desktop = desktop
        self.config = validate_config(config if config is not None else DEFAULT_CONFIG)
        self.targets = {}
        self.selected = None
        self.preferences = dict(preferences or {})

    def bind(self, harness, window):
        if not matches_window(harness, window, self.config):
            raise ValueError("Choose a window showing that harness")
        hwnd, process, _ = window[:3]
        identity = self.desktop.identity(hwnd)
        if not identity:
            raise ValueError("Window is no longer available; refresh the list")
        if any(name != harness and target[0] == hwnd for name, target in self.targets.items()):
            raise ValueError("Use a separate window for each harness")
        self.targets[harness] = (hwnd, identity)
        self.preferences[harness] = process
        if self.selected == harness:
            self.selected = None

    def reconnect(self):
        available = self.desktop.windows()
        for harness in self.config['apps']:
            candidates = [x for x in available if matches_window(harness, x, self.config)
                          and x[1] == self.preferences.get(harness, x[1])]
            current = self.targets.get(harness)
            if current and any(x[0] == current[0] for x in candidates) and self.desktop.identity(current[0]) == current[1]:
                continue
            self.targets.pop(harness, None)
            if self.selected == harness:
                self.selected = None
            if len(candidates) == 1:
                try:
                    self.bind(harness, candidates[0])
                except ValueError:
                    pass  # The window may close between enumeration and binding.
        return available

    def target(self, harness):
        target = self.targets.get(harness)
        if not target or self.desktop.identity(target[0]) != target[1]:
            raise ValueError(f"Open one {harness.title()} window, or choose it in the router")
        return target

    def select(self, harness):
        self.selected = None
        self.reconnect()
        hwnd, _ = self.target(harness)
        self.desktop.activate(hwnd)
        if self.desktop.foreground() != hwnd:
            raise ValueError("Windows did not focus the target; select it and try again")
        self.selected = harness

    def action(self, action):
        self.reconnect()
        if action not in self.config['hotkeys'] or self.selected not in self.config['apps']:
            raise ValueError("Select an app with its selector key or Focus button first")
        hwnd, identity = self.target(self.selected)
        if self.desktop.foreground() != hwnd:
            raise ValueError("Focus changed; select the harness again")
        if self.desktop.modifiers_down():
            raise ValueError("Release Ctrl, Alt, Shift and Windows keys first")
        shortcut = self.config['apps'][self.selected]['shortcuts'].get(action, '')
        if not shortcut:
            raise ValueError('That action has no shortcut configured for this app')
        keys = shortcut_keys(shortcut)
        self.desktop.send(keys, hwnd, identity)


class Win32:
    def __init__(self):
        if os.name != "nt":
            raise RuntimeError("The router requires Windows")
        self.user = ctypes.WinDLL("user32", use_last_error=True)
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        signatures = {
            "IsWindow": ([w.HWND], w.BOOL),
            "IsWindowVisible": ([w.HWND], w.BOOL),
            "GetForegroundWindow": ([], w.HWND),
            "SetForegroundWindow": ([w.HWND], w.BOOL),
            "SendMessageTimeoutW": ([w.HWND, w.UINT, w.WPARAM, w.LPARAM, w.UINT, w.UINT,
                                     ctypes.POINTER(ctypes.c_size_t)], ctypes.c_ssize_t),
            "IsIconic": ([w.HWND], w.BOOL),
            "ShowWindow": ([w.HWND, ctypes.c_int], w.BOOL),
            "GetWindowTextW": ([w.HWND, w.LPWSTR, ctypes.c_int], ctypes.c_int),
            "FindWindowW": ([w.LPCWSTR, w.LPCWSTR], w.HWND),
            "GetWindowThreadProcessId": ([w.HWND, ctypes.POINTER(w.DWORD)], w.DWORD),
            "GetAsyncKeyState": ([ctypes.c_int], ctypes.c_short),
            "RegisterHotKey": ([w.HWND, ctypes.c_int, w.UINT, w.UINT], w.BOOL),
            "UnregisterHotKey": ([w.HWND, ctypes.c_int], w.BOOL),
            "PeekMessageW": ([ctypes.POINTER(w.MSG), w.HWND, w.UINT, w.UINT, w.UINT], w.BOOL),
            "GetMessageW": ([ctypes.POINTER(w.MSG), w.HWND, w.UINT, w.UINT], ctypes.c_int),
            "PostThreadMessageW": ([w.DWORD, w.UINT, w.WPARAM, w.LPARAM], w.BOOL),
            "SendInput": ([w.UINT, ctypes.c_void_p, ctypes.c_int], w.UINT),
        }
        for name, (args, result) in signatures.items():
            fn = getattr(self.user, name)
            fn.argtypes, fn.restype = args, result
        self.kernel.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
        self.kernel.OpenProcess.restype = w.HANDLE
        self.kernel.CloseHandle.argtypes = [w.HANDLE]
        self.kernel.CloseHandle.restype = w.BOOL
        self.kernel.GetProcessTimes.argtypes = [w.HANDLE] + [ctypes.POINTER(w.FILETIME)] * 4
        self.kernel.GetProcessTimes.restype = w.BOOL
        self.kernel.QueryFullProcessImageNameW.argtypes = [w.HANDLE, w.DWORD, w.LPWSTR, ctypes.POINTER(w.DWORD)]
        self.kernel.QueryFullProcessImageNameW.restype = w.BOOL
        self.kernel.GetPackageFamilyName.argtypes = [w.HANDLE, ctypes.POINTER(w.DWORD), w.LPWSTR]
        self.kernel.GetPackageFamilyName.restype = w.LONG
        self.kernel.GetCurrentThreadId.argtypes = []
        self.kernel.GetCurrentThreadId.restype = w.DWORD
        self.kernel.CreateMutexW.argtypes = [ctypes.c_void_p, w.BOOL, w.LPCWSTR]
        self.kernel.CreateMutexW.restype = w.HANDLE
        self.callback_type = ctypes.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)
        self.user.EnumWindows.argtypes = [self.callback_type, w.LPARAM]
        self.user.EnumWindows.restype = w.BOOL
        self.registered = []
        self.events = queue.Queue(maxsize=64)
        self.worker = None
        self.thread_id = None
        self.failure = None
        self.instance = None
        self.hotkeys = dict(HOTKEYS)

    def claim_instance(self):
        ctypes.set_last_error(0)
        handle = self.kernel.CreateMutexW(None, False, r"Local\UniversalMicroRouter")
        if not handle:
            raise ctypes.WinError(ctypes.get_last_error())
        if ctypes.get_last_error() == 183:
            self.kernel.CloseHandle(handle)
            return False
        self.instance = handle
        return True

    def show_existing(self):
        hwnd = self.user.FindWindowW(None, "Universal Micro")
        if hwnd:
            self.activate(hwnd)

    def process(self, hwnd):
        if not self.user.IsWindow(hwnd):
            return None
        pid = w.DWORD()
        self.user.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        handle = self.kernel.OpenProcess(0x1000, False, pid.value)
        if not handle:
            return None
        try:
            times = [w.FILETIME() for _ in range(4)]
            if not self.kernel.GetProcessTimes(handle, *[ctypes.byref(x) for x in times]):
                return None
            path, size = ctypes.create_unicode_buffer(32768), w.DWORD(32768)
            if not self.kernel.QueryFullProcessImageNameW(handle, 0, path, ctypes.byref(size)):
                return None
            born = times[0].dwHighDateTime << 32 | times[0].dwLowDateTime
            family, length = ctypes.create_unicode_buffer(256), w.DWORD(256)
            packaged = self.kernel.GetPackageFamilyName(handle, ctypes.byref(length), family) == 0
            return (pid.value, born), Path(path.value).name.lower(), family.value if packaged else None
        finally:
            self.kernel.CloseHandle(handle)

    def identity(self, hwnd):
        process = self.process(hwnd)
        return process[0] if process else None

    def foreground(self):
        return self.user.GetForegroundWindow()

    def activate(self, hwnd):
        if self.user.IsIconic(hwnd):
            self.user.ShowWindow(hwnd, 9)
        self.user.SetForegroundWindow(hwnd)
        # Cross-queue activation is asynchronous; WM_NULL waits for its processing.
        result = ctypes.c_size_t()
        if not self.user.SendMessageTimeoutW(hwnd, 0, 0, 0, 2, 1000, ctypes.byref(result)):
            raise ValueError("Target did not respond; select it and try again")

    def modifiers_down(self):
        return any(self.user.GetAsyncKeyState(key) & 0x8000 for key in (0x10, 0x11, 0x12, 0x5B, 0x5C))

    def windows(self):
        result = []

        @self.callback_type
        def collect(hwnd, _):
            if not self.user.IsWindowVisible(hwnd):
                return True
            title = ctypes.create_unicode_buffer(1024)
            self.user.GetWindowTextW(hwnd, title, len(title))
            process = self.process(hwnd) if title.value else None
            if process:
                result.append((hwnd, process[1], title.value, process[2]))
            return True

        self.user.EnumWindows(collect, 0)
        return result

    def send(self, keys, hwnd, identity):
        # Windows serializes this input batch; recheck immediately before insertion.
        if self.foreground() != hwnd or self.identity(hwnd) != identity or self.modifiers_down():
            raise ValueError("Target changed before dispatch; nothing sent")

        class Keyboard(ctypes.Structure):
            _fields_ = [("vk", w.WORD), ("scan", w.WORD), ("flags", w.DWORD),
                        ("time", w.DWORD), ("extra", ctypes.c_size_t)]

        class Mouse(ctypes.Structure):
            _fields_ = [("x", w.LONG), ("y", w.LONG), ("data", w.DWORD),
                        ("flags", w.DWORD), ("time", w.DWORD), ("extra", ctypes.c_size_t)]

        class Payload(ctypes.Union):
            _fields_ = [("keyboard", Keyboard), ("mouse", Mouse)]

        class Input(ctypes.Structure):
            _fields_ = [("type", w.DWORD), ("payload", Payload)]

        values = [key_code(key) for key in keys]
        events = [Input(1, Payload(keyboard=Keyboard(vk=key))) for key in values]
        releases = [Input(1, Payload(keyboard=Keyboard(vk=key, flags=2))) for key in reversed(values)]
        batch = (Input * (len(events) + len(releases)))(*events, *releases)
        if self.user.SendInput(len(batch), batch, ctypes.sizeof(Input)) != len(batch):
            release_batch = (Input * len(releases))(*releases)
            self.user.SendInput(len(release_batch), release_batch, ctypes.sizeof(Input))
            raise OSError("Windows blocked input; keep both apps at the same privilege level")

    def register(self, mapping=None):
        self.hotkeys = dict(HOTKEYS if mapping is None else mapping)
        self.failure = None
        self.events = queue.Queue(maxsize=64)
        ready = threading.Event()

        def listen():
            self.thread_id = self.kernel.GetCurrentThreadId()
            message = w.MSG()
            try:
                # Tk consumes thread messages; this thread owns registration and delivery.
                self.user.PeekMessageW(ctypes.byref(message), None, 0, 0, 0)
                for number in self.hotkeys:
                    if not self.user.RegisterHotKey(None, number, 0x4000, 0x70 + number - 1):
                        raise OSError(f"F{number} is already in use; close the other router or remapper")
                    self.registered.append(number)
                ready.set()
                while True:
                    result = self.user.GetMessageW(ctypes.byref(message), None, 0, 0)
                    if result == 0:
                        break
                    if result == -1:
                        raise OSError("Windows hotkey delivery stopped; restart the router")
                    if message.message == 0x0312 and int(message.wParam) in self.hotkeys:
                        try:
                            self.events.put_nowait(int(message.wParam))
                        except queue.Full:
                            pass
            except Exception as error:
                self.failure = str(error)
            finally:
                for number in self.registered:
                    self.user.UnregisterHotKey(None, number)
                self.registered.clear()
                ready.set()

        self.worker = threading.Thread(target=listen, name="Micro hotkeys", daemon=True)
        self.worker.start()
        if not ready.wait(2):
            self.stop_hotkeys()
            raise OSError("Windows hotkey registration timed out")
        if self.failure:
            self.stop_hotkeys()
            raise OSError(self.failure)

    def pending(self):
        if self.failure:
            raise OSError(self.failure)
        while True:
            try:
                yield self.events.get_nowait()
            except queue.Empty:
                return

    def stop_hotkeys(self):
        if self.worker and self.worker.is_alive() and self.thread_id:
            self.user.PostThreadMessageW(self.thread_id, 0x0012, 0, 0)
            self.worker.join(timeout=2)
            if self.worker.is_alive():
                raise OSError('Hotkey thread did not stop; configuration was not applied')
        self.worker, self.thread_id = None, None

    def replace_hotkeys(self, mapping):
        previous = dict(self.hotkeys)
        self.stop_hotkeys()
        try:
            self.register(mapping)
        except OSError as error:
            try:
                self.register(previous)
            except OSError as restore_error:
                self.failure = f'{error}; previous keys could not be restored. Routing is paused'
                raise OSError(self.failure) from restore_error
            raise

    def close(self):
        self.stop_hotkeys()
        if self.instance:
            self.kernel.CloseHandle(self.instance)
            self.instance = None


def reconfigure(router, candidate, path=PROFILES_PATH):
    candidate = validate_config(candidate)
    prefs = {h:p for h,p in router.preferences.items()
             if h in candidate['apps'] and p in candidate['apps'][h]['processes']}
    replacement = Router(router.desktop, prefs, candidate)
    previous_keys = hotkeys(router.config)
    router.desktop.replace_hotkeys(hotkeys(candidate))
    try:
        save_profiles(path, candidate)
    except (OSError, ValueError):
        try:
            router.desktop.replace_hotkeys(previous_keys)
        except OSError as error:
            router.desktop.stop_hotkeys()
            router.desktop.failure = 'Profiles could not be saved and keys could not be restored. Routing is paused'
            raise OSError(router.desktop.failure) from error
        raise
    return replacement


def main():
    import tkinter as tk
    from tkinter import ttk
    from profiles import edit_profiles
    config = load_profiles()
    desktop = Win32()
    if not desktop.claim_instance():
        try:
            if "--background" not in sys.argv:
                desktop.show_existing()
        finally:
            desktop.close()
        return
    root = tk.Tk()
    root.title("Universal Micro")
    root.geometry("1040x540")
    rows = {}
    editing = False
    try:
        path = BINDINGS_PATH if BINDINGS_PATH.exists() else Path(__file__).resolve().parent / '.local/bindings.json'
        preferences = load_bindings(path, config)
        initial_status = "Select an app using its key or Focus. Missing windows reconnect automatically."
    except (OSError, ValueError) as error:
        preferences, initial_status = {}, str(error)
    router = Router(desktop, preferences, config)
    saved = dict(preferences)
    status = tk.StringVar(value=initial_status)
    ttk.Label(root, text="Universal Micro", font=("Segoe UI", 17)).pack(anchor="w", padx=18, pady=(16,4))
    ttk.Label(root, text="Add apps/windows and edit shortcuts in Apps & shortcuts. Keep browser apps in dedicated windows.").pack(anchor="w", padx=18)
    holder = ttk.Frame(root)
    holder.pack(fill='both', expand=True, padx=18, pady=12)
    canvas = tk.Canvas(holder, highlightthickness=0, height=210)
    scrollbar = ttk.Scrollbar(holder, orient='vertical', command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y')
    canvas.pack(side='left', fill='both', expand=True)
    frame = ttk.Frame(canvas)
    frame_id = canvas.create_window((0,0), window=frame, anchor='nw')
    frame.bind('<Configure>', lambda event: canvas.configure(scrollregion=canvas.bbox('all')))
    canvas.bind('<Configure>', lambda event: canvas.itemconfigure(frame_id, width=event.width))
    frame.columnconfigure(1, weight=1)

    def focus(harness):
        try:
            router.select(harness)
            status.set(f"Selected: {config['apps'][harness]['name']}")
        except (ValueError, OSError) as error:
            status.set(str(error))

    def bind(harness):
        combo, candidates, label = rows[harness]
        try:
            index = combo.current()
            if index < 0:
                raise ValueError("Choose a window first")
            router.bind(harness, candidates[index])
            save_bindings(BINDINGS_PATH, router.preferences)
            saved.clear()
            saved.update(router.preferences)
            label.config(text="Connected")
            status.set(f"{config['apps'][harness]['name']} bound. Select it before an action.")
        except (ValueError, OSError) as error:
            status.set(str(error))

    def build_rows():
        for child in frame.winfo_children():
            child.destroy()
        rows.clear()
        for row, (harness, app) in enumerate(config['apps'].items()):
            ttk.Label(frame, text=f"{app['selector'] or '—'}  {app['name']}", width=20).grid(row=row, column=0, sticky='w', pady=5)
            combo = ttk.Combobox(frame, state='readonly', width=58)
            combo.grid(row=row, column=1, sticky='ew', padx=8)
            ttk.Button(frame, text='Bind', command=lambda h=harness: bind(h)).grid(row=row, column=2)
            ttk.Button(frame, text='Focus', command=lambda h=harness: focus(h)).grid(row=row, column=3, padx=4)
            label = ttk.Label(frame, text='Waiting', width=10)
            label.grid(row=row, column=4, padx=4)
            rows[harness] = (combo, [], label)

    def refresh():
        previous = router.selected
        available = router.reconnect()
        if previous and router.selected is None:
            status.set("Window changed. Select the app again before an action.")
        for harness, (combo, candidates, label) in rows.items():
            old = candidates[combo.current()][0] if 0 <= combo.current() < len(candidates) else None
            candidates[:] = [x for x in available if matches_window(harness, x, config)]
            combo['values'] = [f"{x[2]}  [{x[0]}]" for x in candidates]
            target = router.targets.get(harness)
            choice = old if any(x[0] == old for x in candidates) else target[0] if target else None
            index = next((i for i, x in enumerate(candidates) if x[0] == choice), None)
            combo.current(index) if index is not None else combo.set('')
            label.config(text='Connected' if target else 'Choose' if candidates else 'Waiting')
        if saved != router.preferences:
            try:
                save_bindings(BINDINGS_PATH, router.preferences)
                saved.clear()
                saved.update(router.preferences)
            except OSError:
                status.set("Could not save bindings; check the user settings folder permissions.")

    def watch_windows():
        if not editing:
            refresh()
        root.after(1500, watch_windows)

    def apply_config(candidate):
        nonlocal config, router
        router = reconfigure(router, candidate)
        config = router.config
        saved.clear()
        build_rows()
        refresh()
        action_summary.set('   '.join(f'{key or "—"} {name}' for name,key in config['hotkeys'].items()))
        status.set("Profiles saved. Select an app again before an action.")

    def configure():
        nonlocal editing
        editing = True
        try:
            edit_profiles(root, config, apply_config, desktop.windows)
        finally:
            editing = False

    buttons = ttk.Frame(root)
    buttons.pack(fill='x', padx=18)
    ttk.Button(buttons, text="Apps & shortcuts…", command=configure).pack(side='left')
    ttk.Button(buttons, text="Refresh windows", command=refresh).pack(side='left', padx=8)
    action_summary = tk.StringVar(value='   '.join(f'{key or "—"} {name}' for name,key in config['hotkeys'].items()))
    ttk.Label(root, textvariable=action_summary, wraplength=980).pack(anchor='w', padx=18, pady=(12,4))
    ttk.Label(root, textvariable=status, wraplength=980).pack(anchor='w', padx=18)
    ttk.Label(root, text="Fallback: use the Micro touch sensor to return to native Layer 1.").pack(anchor='w', padx=18, pady=8)
    startup = tk.BooleanVar(value=startup_enabled())

    def toggle_startup():
        try:
            set_startup(startup.get())
            status.set("Startup enabled at Windows sign-in." if startup.get() else "Startup disabled.")
        except (OSError, ValueError) as error:
            startup.set(startup_enabled())
            status.set(str(error))

    ttk.Checkbutton(root, text="Start at Windows sign-in", variable=startup, command=toggle_startup).pack(anchor='w', padx=18, pady=(4,12))

    def poll():
        try:
            pending = list(desktop.pending())
            if not editing:
                for number in pending:
                    binding = hotkeys(config).get(number)
                    if not binding:
                        continue
                    kind, name = binding
                    try:
                        if kind == 'select':
                            focus(name)
                        else:
                            router.action(name)
                            status.set(f"{config['apps'][router.selected]['name']}: {name} shortcut sent")
                    except (ValueError, OSError) as error:
                        status.set(str(error))
                        root.bell()
        except OSError as error:
            if not editing:
                status.set(f"{error}. Open Apps & shortcuts to choose another input key.")
        root.after(30, poll)

    def close():
        desktop.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close)
    build_rows()
    try:
        ready = True
        try:
            desktop.register(hotkeys(config))
        except OSError as error:
            ready = False
            status.set(f"{error}. Open Apps & shortcuts to choose another input key.")
        watch_windows()
        poll()
        if "--background" in sys.argv and ready:
            root.iconify()
        root.mainloop()
    finally:
        desktop.close()


def show_error(message):
    user = ctypes.WinDLL("user32", use_last_error=True)
    user.MessageBoxW.argtypes = [w.HWND, w.LPCWSTR, w.LPCWSTR, w.UINT]
    user.MessageBoxW.restype = ctypes.c_int
    user.MessageBoxW(None, message, "Universal Micro", 0x10)


def run():
    try:
        main()
    except Exception as error:
        show_error(f"Could not start Universal Micro.\n\n{error}\n\nCheck Python/Tk, close other routers, and launch from a console for troubleshooting.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
