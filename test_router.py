"""Small runnable regression check: python test_router.py."""
import unittest
import sys
import json
from pathlib import Path
import os
import tempfile
from unittest.mock import patch

from router import Router


class RouterCheck(unittest.TestCase):
    def test_codex_requires_verified_package_identity(self):
        from router import matches_window
        self.assertFalse(matches_window("codex", (1, "chatgpt.exe", "Codex")))
        self.assertFalse(matches_window("codex", (1, "chatgpt.exe", "Codex", "OpenAI.ChatGPT_example")))
        self.assertTrue(matches_window("codex", (1, "chatgpt.exe", "Any project", "OpenAI.Codex_2p2nqsd0c76g0")))

    def test_startup_never_changes_another_installations_entry(self):
        import types
        from contextlib import nullcontext
        import router
        values = {router.RUN_VALUE: ('"old install" --background', 1), "Unrelated": ("keep", 1)}
        registry = types.SimpleNamespace(HKEY_CURRENT_USER=1, REG_SZ=1,
            CreateKey=lambda *a: nullcontext(1), OpenKey=lambda *a: nullcontext(1),
            QueryValueEx=lambda key, name: values[name],
            SetValueEx=lambda key, name, reserved, kind, value: values.update({name: (value, kind)}),
            DeleteValue=lambda key, name: values.pop(name))
        with patch.dict(sys.modules, {"winreg": registry}), patch.object(router, "startup_command", return_value='"this install" --background'):
            before = dict(values)
            for enabled in (True, False):
                with self.assertRaises(ValueError):
                    router.set_startup(enabled)
                self.assertEqual(values, before)
            values[router.RUN_VALUE] = ('"this install" --background', 1)
            router.set_startup(False)
            self.assertEqual(values, {"Unrelated": ("keep", 1)})

    def test_startup_failure_is_visible_without_a_console(self):
        import router
        self.assertTrue(callable(getattr(router, "run", None)))
        with patch.object(router, "main", side_effect=RuntimeError("Hotkeys unavailable")), patch.object(router, "show_error") as notice:
            self.assertEqual(router.run(), 1)
            self.assertIn("Hotkeys unavailable", notice.call_args.args[0])

    def test_reconnect_uses_app_identity_and_refuses_ambiguous_windows(self):
        from router import matches_window

        class Desktop:
            records = [(10, "chrome.exe", "First — Hermes - Google Chrome"),
                       (20, "chrome.exe", "project - Pi Web - Google Chrome"),
                       (30, "chatgpt.exe", "Codex", "OpenAI.Codex_2p2nqsd0c76g0"),
                       (40, "chrome.exe", "Hermes documentation - Google Chrome")]
            identities = {10: (1, 100), 20: (1, 100), 30: (2, 200), 40: (1, 100)}
            current = 20

            def windows(self):
                return self.records

            def identity(self, hwnd):
                return self.identities.get(hwnd)

            def foreground(self):
                return self.current

            def activate(self, hwnd):
                self.current = hwnd

        desktop = Desktop()
        router = Router(desktop, {"pi": "chrome.exe"})
        router.reconnect()
        self.assertEqual({h: t[0] for h, t in router.targets.items()}, {"hermes": 10, "pi": 20, "codex": 30})
        router.select("pi")
        # The old HWND is reused by an unrelated page; the app comes back in a new process/window.
        desktop.records = [(20, "chrome.exe", "Unrelated - Google Chrome"),
                           (21, "chrome.exe", "Different project - Pi Web - Google Chrome")]
        desktop.identities = {20: (9, 900), 21: (9, 900)}
        router.reconnect()
        self.assertIsNone(router.selected)
        self.assertEqual(router.target("pi")[0], 21)
        with self.assertRaises(ValueError):
            router.action("send")
        # A saved browser preference survives restart; two matching windows require a choice.
        desktop.records.append((22, "chrome.exe", "Other - Pi Web - Google Chrome"))
        desktop.identities[22] = (9, 900)
        restarted = Router(desktop, router.preferences)
        restarted.reconnect()
        self.assertNotIn("pi", restarted.targets)
        restarted.bind("pi", desktop.records[-1])
        restarted.reconnect()
        self.assertEqual(restarted.target("pi")[0], 22)
        desktop.records = [(23, "msedge.exe", "Pi Web - Microsoft Edge")]
        desktop.identities = {23: (3, 300)}
        restarted.reconnect()
        self.assertNotIn("pi", restarted.targets)
        self.assertTrue(matches_window("pi", (23, "msedge.exe", "Pi Web - Microsoft Edge")))
        self.assertFalse(matches_window("pi", (24, "other.exe", "Pi Web")))
        self.assertFalse(matches_window("hermes", (25, "chrome.exe", "Not Hermes - Google Chrome")))

    def test_saved_bindings_keep_only_valid_process_preferences(self):
        from router import load_bindings, save_bindings
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bindings.json"
            self.assertEqual(load_bindings(path), {})
            preferences = {"codex": "chatgpt.exe", "hermes": "chrome.exe", "pi": "msedge.exe"}
            save_bindings(path, preferences)
            self.assertEqual(load_bindings(path), preferences)
            path.write_text('{"pi":"unrelated.exe"}')
            with self.assertRaises(ValueError):
                load_bindings(path)

    @unittest.skipUnless(os.name == "nt", "Windows single-instance check")
    def test_single_instance_lock_is_released(self):
        from router import Win32
        first, second, third = Win32(), Win32(), Win32()
        # Isolated kernel objects: the real router may be running during this check.
        for desktop in (first, second, third):
            native = desktop.kernel.CreateMutexW
            desktop.kernel.CreateMutexW = lambda a, b, name, native=native: native(a, b, rf"Local\UniversalMicroTest-{os.getpid()}")
        try:
            self.assertTrue(first.claim_instance())
            self.assertFalse(second.claim_instance())
            first.close()
            self.assertTrue(third.claim_instance())
        finally:
            first.close()
            second.close()
            third.close()

    def test_activation_waits_for_the_target_message_queue(self):
        from router import Win32

        class User:
            foreground = 10
            responds = True

            def IsIconic(self, hwnd):
                return False

            def SetForegroundWindow(self, hwnd):
                self.pending = hwnd  # Windows completes cross-queue activation asynchronously.
                return True

            def SendMessageTimeoutW(self, hwnd, message, *args):
                if not self.responds:
                    return 0
                self.foreground = self.pending
                return 1

        desktop = object.__new__(Win32)
        desktop.user = User()
        desktop.activate(20)
        self.assertEqual(desktop.user.foreground, 20)
        desktop.user.responds = False
        with self.assertRaises(ValueError):
            desktop.activate(20)

    @unittest.skipUnless(os.name == "nt", "Windows message-loop check")
    def test_hotkeys_survive_the_tk_message_loop(self):
        import tkinter as tk
        from ctypes import wintypes as w
        from router import Win32
        root = tk.Tk()
        root.withdraw()
        desktop = Win32()
        # Keep real worker/message delivery; never acquire the hardware's global keys.
        desktop.user.RegisterHotKey = lambda *args: True
        desktop.user.UnregisterHotKey = lambda *args: True
        received = []
        try:
            desktop.register()
            thread_id = getattr(desktop, "thread_id", desktop.kernel.GetCurrentThreadId())
            desktop.user.PostThreadMessageW.argtypes = [w.DWORD, w.UINT, w.WPARAM, w.LPARAM]
            desktop.user.PostThreadMessageW.restype = w.BOOL
            root.after(0, lambda: desktop.user.PostThreadMessageW(thread_id, 0x0312, 22, 0))
            root.after(100, lambda: received.extend(desktop.pending()))
            root.after(150, root.quit)
            root.mainloop()
            self.assertEqual(received, [22])
        finally:
            desktop.close()
            root.destroy()

    def test_input_layer_matches_exactly_the_registered_router_keys(self):
        from router import HOTKEYS
        layer = json.loads((Path(__file__).parent / "input/Universal-Micro-layer.json").read_text())
        self.assertEqual(layer["keyboard"], "codex_micro")
        matrix = layer["layer"]["layout"]["base"]
        self.assertEqual(list(map(len, matrix)), [2, 4, 4, 3])
        assigned = [key["keycode"] for row in matrix for key in row if key["keycode"] != "KC_NONE"]
        self.assertEqual(set(assigned), {f"KC_F{number}" for number in HOTKEYS})
        self.assertEqual(len(assigned), len(HOTKEYS))
        self.assertFalse(layer["actions"] or layer["smartActions"] or layer["multiactions"])

    def test_only_dispatches_to_the_selected_live_foreground_process(self):
        class Desktop:
            current = 10
            identities = {10: (1, 100), 20: (2, 200)}
            sent = []

            def identity(self, hwnd):
                return self.identities.get(hwnd)

            def windows(self):
                return [(10, "chrome.exe", "Pi Web - Google Chrome"),
                        (20, "chrome.exe", "Untitled — Hermes - Google Chrome")]

            def foreground(self):
                return self.current

            def modifiers_down(self):
                return False

            def activate(self, hwnd):
                self.current = hwnd

            def send(self, keys, hwnd, identity):
                assert self.foreground() == hwnd and self.identity(hwnd) == identity
                self.sent.append(keys)

        desktop = Desktop()
        router = Router(desktop)
        with self.assertRaises(ValueError):
            router.action("send")
        router.bind("pi", desktop.windows()[0])
        with self.assertRaises(ValueError):
            router.bind("hermes", desktop.windows()[0])
        router.bind("hermes", desktop.windows()[1])
        router.select("pi")
        router.action("dictate")
        self.assertEqual(desktop.sent[-1], ("CTRL", "ALT", "SHIFT", "R"))
        with self.assertRaises(ValueError):
            router.select("codex")
        with self.assertRaises(ValueError):
            router.action("send")
        router.select("pi")
        desktop.current = 20
        with self.assertRaises(ValueError):
            router.action("send")
        router.select("pi")
        desktop.identities[10] = (1, 999)  # Same HWND and PID, different process lifetime.
        with self.assertRaises(ValueError):
            router.action("new")
        self.assertEqual(len(desktop.sent), 1)
        desktop.identities[10] = (1, 100)
        router.select("pi")
        desktop.modifiers_down = lambda: True
        with self.assertRaises(ValueError):
            router.action("stop")
        self.assertEqual(router.selected, "pi")
        desktop.modifiers_down = lambda: False
        desktop.windows = lambda: [(10, "chrome.exe", "Unrelated - Google Chrome")]
        with self.assertRaises(ValueError):
            router.action("send")
        self.assertIsNone(router.selected)
        self.assertEqual(len(desktop.sent), 1)


def native_check():
    """Send a chord only to a temporary window owned by this check."""
    import ctypes
    import tkinter as tk
    from ctypes import wintypes as w
    from router import Win32, WEB_KEYS

    root = tk.Tk()
    root.title("Universal Micro isolated input check")
    root.geometry("480x140+100+100")
    tk.Label(root, text="Press F12 here to run the isolated shortcut check.").pack(padx=30, pady=30)
    root.update()
    desktop = Win32()
    desktop.user.GetAncestor.argtypes = [w.HWND, w.UINT]
    desktop.user.GetAncestor.restype = w.HWND
    hwnd = desktop.user.GetAncestor(root.winfo_id(), 2)
    desktop.user.GetWindowRect.argtypes = [w.HWND, ctypes.POINTER(w.RECT)]
    bounds = w.RECT()
    desktop.user.GetWindowRect(hwnd, ctypes.byref(bounds))
    print("Test window:", {"mapped": root.winfo_ismapped(), "visible": bool(desktop.user.IsWindowVisible(hwnd)),
          "bounds": (bounds.left, bounds.top, bounds.right, bounds.bottom)}, flush=True)
    received, errors = [], []
    root.bind("<KeyPress>", lambda event: received.append((event.keysym, event.state)))

    def send():
        try:
            desktop.send(WEB_KEYS["hermes"]["dictate"], hwnd, desktop.identity(hwnd))
        except Exception as error:
            errors.append(error)
        root.after(350, root.quit)

    root.bind("<F12>", lambda _: root.after(50, send))
    root.after(60000, root.quit)
    try:
        root.mainloop()
    finally:
        root.destroy()
    if errors:
        raise errors[0]
    assert any(key.lower() == "d" and state & 5 == 5 and state & 0x20008 for key, state in received), received
    print("Native check: Ctrl+Alt+Shift+D reached the owned test window.")


if __name__ == "__main__":
    if "--native" in sys.argv:
        native_check()
    else:
        unittest.main()
