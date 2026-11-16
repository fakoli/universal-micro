"""Configuration and dispatch checks use private temporary files and fake targets."""
import copy
from pathlib import Path
import tempfile
import unittest


class ProfileCheck(unittest.TestCase):
    def test_defaults_and_invalid_configuration(self):
        from profiles import DEFAULT_CONFIG, validate_config, shortcut_keys, key_code, hotkeys
        self.assertEqual(shortcut_keys('Control + shift + d'), ('CTRL', 'SHIFT', 'D'))
        self.assertEqual(key_code('F24'), 0x87)
        self.assertEqual(hotkeys(DEFAULT_CONFIG)[16], ('select', 'claude'))
        for change in ('duplicate', 'package', 'key', 'process', 'uppercase', 'null', 'loop', 'shape'):
            data = copy.deepcopy(DEFAULT_CONFIG)
            if change == 'duplicate': data['apps']['claude']['selector'] = 'F19'
            if change == 'package': data['apps']['codex']['package'] = ''
            if change == 'key': data['apps']['claude']['shortcuts']['send'] = 'run arbitrary text'
            if change == 'process': data['apps']['claude']['processes'] = ['*']
            if change == 'uppercase': data['apps']['claude']['processes'] = ['Claude.exe']
            if change == 'null': data['hotkeys']['send'] = None
            if change == 'loop': data['apps']['claude']['shortcuts']['send'] = 'F19'
            if change == 'shape': data['apps']['claude'] = {}
            with self.assertRaises(ValueError): validate_config(data)

    def test_save_load_custom_windows_and_actions(self):
        from profiles import DEFAULT_CONFIG, load_profiles, save_profiles
        data = copy.deepcopy(DEFAULT_CONFIG)
        data['hotkeys']['steer'] = 'F23'
        data['apps']['claude-work'] = copy.deepcopy(data['apps']['claude'])
        data['apps']['claude-work'].update(name='Claude Work', selector='F17', title_mode='contains', title='Work')
        data['apps']['claude-work']['shortcuts']['steer'] = 'CTRL+ENTER'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'profiles.json'
            self.assertEqual(load_profiles(path), DEFAULT_CONFIG)
            save_profiles(path, data)
            self.assertEqual(load_profiles(path), data)
            large = copy.deepcopy(data)
            large['apps'] = {f'app{n}':dict(data['apps']['claude'], selector='', title='界'*512, package='x'*256) for n in range(32)}
            before = path.read_bytes()
            with self.assertRaises(ValueError): save_profiles(path, large)
            self.assertEqual(path.read_bytes(), before)
            invalid = '{"version":1,"version":2}'
            path.write_text(invalid)
            with self.assertRaises(ValueError): load_profiles(path)
            self.assertEqual(path.read_text(), invalid)

    def test_reconfigure_rolls_back_on_save_failure(self):
        from unittest.mock import patch
        from profiles import DEFAULT_CONFIG, hotkeys
        from router import Router, reconfigure, matches_window
        class Desktop:
            keys = hotkeys(DEFAULT_CONFIG)
            def replace_hotkeys(self, keys): self.keys = keys
        desktop = Desktop()
        original = Router(desktop)
        original.selected = 'claude'
        candidate = copy.deepcopy(DEFAULT_CONFIG)
        candidate['apps']['claude']['selector'] = 'F17'
        for error in (OSError('Read only'), ValueError('Cannot serialize configuration')):
            with patch('router.save_profiles', side_effect=error):
                with self.assertRaises(type(error)): reconfigure(original, candidate)
            self.assertEqual(desktop.keys, hotkeys(DEFAULT_CONFIG))
        self.assertEqual(original.selected, 'claude')
        with tempfile.TemporaryDirectory() as directory:
            replacement = reconfigure(original, candidate, Path(directory) / 'profiles.json')
            self.assertIsNone(replacement.selected)
            self.assertEqual(desktop.keys[17], ('select', 'claude'))
        candidate['apps']['claude'].update(processes=['chrome.exe'], title_mode='exact', title='Test - Google Chrome')
        self.assertTrue(matches_window('claude', (1,'chrome.exe','Test - Google Chrome'), candidate))

    def test_custom_window_dispatch_and_disabled_action(self):
        from profiles import DEFAULT_CONFIG
        from router import Router
        data = copy.deepcopy(DEFAULT_CONFIG)
        data['apps'] = {'work': dict(data['apps']['claude'], name='Work', selector='F17', title_mode='contains', title='Work')}
        data['hotkeys']['steer'] = 'F23'
        data['apps']['work']['shortcuts'] = {'send': 'ENTER', 'steer': 'CTRL+ENTER'}
        class Desktop:
            current = 1
            sent = []
            def windows(self): return [(1,'claude.exe','Personal'), (2,'claude.exe','Work')]
            def identity(self, hwnd): return (hwnd, 100)
            def activate(self, hwnd): self.current = hwnd
            def foreground(self): return self.current
            def modifiers_down(self): return False
            def send(self, keys, hwnd, identity): self.sent.append((keys, hwnd))
        desktop = Desktop()
        router = Router(desktop, config=data)
        router.select('work')
        router.action('steer')
        self.assertEqual(desktop.sent, [(('CTRL','ENTER'),2)])
        with self.assertRaises(ValueError): router.action('dictate')


if __name__ == '__main__': unittest.main()
