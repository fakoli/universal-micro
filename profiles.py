"""User-owned app profiles and shortcut validation; no executable commands."""
import copy
import json
import os
from pathlib import Path
import re

STATE_DIR = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData/Local')) / 'UniversalMicro'
PROFILES_PATH = STATE_DIR / 'profiles.json'
CODEX_PACKAGE = 'OpenAI.Codex_2p2nqsd0c76g0'
DEFAULT_CONFIG = {
    'version': 1,
    'hotkeys': {'dictate':'F19', 'send':'F20', 'stop':'F21', 'new':'F22'},
    'apps': {
        'codex': {'name':'Codex', 'selector':'F13', 'processes':['chatgpt.exe','codex.exe'], 'package':CODEX_PACKAGE,
                  'title_mode':'any', 'title':'', 'shortcuts':{'dictate':'CTRL+SHIFT+D','send':'CTRL+ENTER','stop':'ESC','new':'CTRL+N'}},
        'hermes': {'name':'Hermes', 'selector':'F14', 'processes':['chrome.exe','msedge.exe'], 'package':'',
                   'title_mode':'app', 'title':'Hermes', 'shortcuts':{'dictate':'CTRL+ALT+SHIFT+D','send':'CTRL+ALT+SHIFT+ENTER','stop':'CTRL+ALT+SHIFT+X','new':'CTRL+ALT+SHIFT+N'}},
        'pi': {'name':'Pi', 'selector':'F15', 'processes':['chrome.exe','msedge.exe'], 'package':'',
               'title_mode':'app', 'title':'Pi Web', 'shortcuts':{'dictate':'CTRL+ALT+SHIFT+R','send':'CTRL+ALT+SHIFT+S','stop':'CTRL+ALT+SHIFT+T','new':'CTRL+ALT+SHIFT+C'}},
        'claude': {'name':'Claude', 'selector':'F16', 'processes':['claude.exe'], 'package':'',
                   'title_mode':'app', 'title':'Claude', 'shortcuts':{'dictate':'CTRL+D','send':'ENTER','stop':'ESC','new':'CTRL+N'}},
    },
}
MODIFIERS = {'CTRL':0x11, 'ALT':0x12, 'SHIFT':0x10, 'WIN':0x5B}
KEY_CODES = {**MODIFIERS, 'ENTER':13, 'ESC':27, 'SPACE':32, 'TAB':9, 'BACKSPACE':8, 'DELETE':46,
             'INSERT':45, 'HOME':36, 'END':35, 'PAGEUP':33, 'PAGEDOWN':34,
             'LEFT':37, 'UP':38, 'RIGHT':39, 'DOWN':40, 'PLUS':0xBB, 'MINUS':0xBD}


def key_code(key):
    if key in KEY_CODES:
        return KEY_CODES[key]
    if len(key) == 1 and key in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
        return ord(key)
    if re.fullmatch(r'F(?:[1-9]|1\d|2[0-4])', key):
        return 0x6F + int(key[1:])
    raise ValueError('Use a letter, digit, F1–F24 or a supported named key')


def shortcut_keys(text):
    if not isinstance(text, str) or len(text) > 80:
        raise ValueError('Invalid shortcut')
    aliases = {'CONTROL':'CTRL', 'ESCAPE':'ESC', 'RETURN':'ENTER', 'WINDOWS':'WIN'}
    keys = tuple(aliases.get(key.strip().upper(), key.strip().upper()) for key in text.split('+'))
    if not keys or keys[-1] in MODIFIERS or any(key not in MODIFIERS for key in keys[:-1]) or len(set(keys)) != len(keys):
        raise ValueError('Use modifiers followed by one key, for example CTRL+SHIFT+D')
    for key in keys:
        key_code(key)
    return keys


def hotkeys(config):
    result = {}
    entries = [(app['selector'], ('select', name)) for name, app in config['apps'].items() if app['selector']]
    entries += [(key, ('action', name)) for name, key in config['hotkeys'].items() if key]
    for key, binding in entries:
        if not isinstance(key, str) or not re.fullmatch(r'F(?:1[3-9]|2[0-4])', key):
            raise ValueError('Global input keys must be F13–F24; leave blank to disable')
        number = int(key[1:])
        if number in result:
            raise ValueError(f'{key} is assigned more than once')
        result[number] = binding
    return result


def validate_config(config):
    if not isinstance(config, dict) or set(config) != {'version','apps','hotkeys'} or type(config['version']) is not int or config['version'] != 1:
        raise ValueError('Unsupported profile format; expected version 1')
    apps, actions = config['apps'], config['hotkeys']
    if not isinstance(apps, dict) or not 1 <= len(apps) <= 32 or not isinstance(actions, dict) or not 1 <= len(actions) <= 12:
        raise ValueError('Configure 1–32 apps and 1–12 actions')
    for name in list(apps) + list(actions):
        if not isinstance(name, str) or not re.fullmatch(r'[a-z][a-z0-9_-]{0,39}', name):
            raise ValueError('IDs must start with a lowercase letter and use letters, digits, - or _')
    if any(not isinstance(key, str) for key in actions.values()):
        raise ValueError('Action input keys must be strings; leave blank to disable')
    for name, app in apps.items():
        fields = {'name','selector','processes','package','title_mode','title','shortcuts'}
        if not isinstance(app, dict) or set(app) != fields:
            raise ValueError('App profile has missing or unknown fields')
        if not isinstance(app['name'], str) or not app['name'].strip() or len(app['name']) > 80:
            raise ValueError('App name must contain 1–80 characters')
        processes = app['processes']
        if not isinstance(processes, list) or not 1 <= len(processes) <= 8 or any(
            not isinstance(p, str) or not p.endswith('.exe') or len(p) > 100 or
            any(c in p for c in '<>:"/\\|?*\r\n\0') or p != p.strip() or p != p.lower() for p in processes):
            raise ValueError('Use executable basenames in lowercase, for example claude.exe')
        if not isinstance(app['package'], str) or len(app['package']) > 256:
            raise ValueError('Invalid package family')
        if name == 'codex' and (app['package'] != CODEX_PACKAGE or any(p not in ('chatgpt.exe','codex.exe') for p in processes)):
            raise ValueError('The Codex profile must retain its verified package identity')
        if app['title_mode'] not in ('any','app','exact','contains','suffix') or not isinstance(app['title'], str) or len(app['title']) > 512:
            raise ValueError('Invalid window title rule')
        if app['title_mode'] != 'any' and not app['title'].strip():
            raise ValueError('Enter a nonempty window title pattern')
        shortcuts = app['shortcuts']
        if not isinstance(shortcuts, dict) or set(shortcuts) - set(actions):
            raise ValueError('App shortcuts must refer to configured actions')
        for shortcut in shortcuts.values():
            if shortcut != '':
                shortcut_keys(shortcut)
        if not isinstance(app['selector'], str):
            raise ValueError('Invalid selector key')
    registered = hotkeys(config)
    for app in apps.values():
        for shortcut in app['shortcuts'].values():
            if shortcut:
                keys = shortcut_keys(shortcut)
                if len(keys) == 1 and key_code(keys[0]) - 0x6F in registered:
                    raise ValueError('An output shortcut cannot trigger a registered input key')
    return copy.deepcopy(config)


def load_profiles(path=PROFILES_PATH):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate configuration field')
            result[key] = value
        return result
    try:
        if path.stat().st_size > 65536:
            raise ValueError('Profile file is too large')
        return validate_config(json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_pairs))
    except FileNotFoundError:
        return copy.deepcopy(DEFAULT_CONFIG)


def save_profiles(path, config):
    config = validate_config(config)
    data = (json.dumps(config, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
    if len(data) > 65536:
        raise ValueError('Profile file is too large; shorten title rules or remove unused profiles')
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_bytes(data)
    temporary.replace(path)


def edit_profiles(parent, config, apply, get_windows):
    """Edit a private working copy; only Apply writes configuration or changes routing."""
    import tkinter as tk
    from tkinter import ttk, simpledialog
    draft = copy.deepcopy(config)
    dialog = tk.Toplevel(parent)
    dialog.title('Apps & shortcuts')
    dialog.geometry('760x590')
    dialog.transient(parent)
    dialog.grab_set()
    notebook = ttk.Notebook(dialog)
    notebook.pack(fill='both', expand=True, padx=12, pady=12)
    apps_tab, keys_tab = ttk.Frame(notebook), ttk.Frame(notebook)
    notebook.add(apps_tab, text='Apps and windows')
    notebook.add(keys_tab, text='Action input keys')
    app_list = tk.Listbox(apps_tab, exportselection=False)
    app_list.pack(fill='both', expand=True, padx=10, pady=10)
    status = tk.StringVar()
    ttk.Label(dialog, textvariable=status, wraplength=710).pack(fill='x', padx=12)
    ttk.Label(dialog, text='F13–F24 are global while the router runs. Blank keys disable a binding.\nApp shortcuts never execute scripts or commands.', wraplength=710).pack(anchor='w', padx=12, pady=6)
    action_vars = {}
    action_frame = ttk.Frame(keys_tab)
    action_frame.pack(fill='both', expand=True, padx=10, pady=10)

    def free_key():
        used = {app['selector'] for app in draft['apps'].values()} | set(draft['hotkeys'].values())
        return next((f'F{n}' for n in range(13,25) if f'F{n}' not in used), '')

    def render():
        selected = app_list.curselection()
        app_list.delete(0, 'end')
        for name, app in draft['apps'].items():
            app_list.insert('end', f"{app['selector'] or 'Focus button'}   {app['name']}   [{name}]")
        if draft['apps']:
            app_list.selection_set(min(selected[0] if selected else 0, len(draft['apps']) - 1))
        for child in action_frame.winfo_children(): child.destroy()
        action_vars.clear()
        for row, (name, key) in enumerate(draft['hotkeys'].items()):
            ttk.Label(action_frame, text=name, width=22).grid(row=row, column=0, sticky='w', pady=4)
            variable = tk.StringVar(value=key)
            action_vars[name] = variable
            ttk.Combobox(action_frame, textvariable=variable, values=['']+[f'F{n}' for n in range(13,25)], state='readonly', width=10).grid(row=row, column=1)
            ttk.Button(action_frame, text='Remove', command=lambda a=name: remove_action(a)).grid(row=row, column=2, padx=8)

    def sync_actions():
        for name, variable in action_vars.items(): draft['hotkeys'][name] = variable.get()

    def remove_action(name):
        sync_actions()
        if len(draft['hotkeys']) == 1:
            status.set('Keep at least one action.'); return
        draft['hotkeys'].pop(name)
        for app in draft['apps'].values(): app['shortcuts'].pop(name, None)
        render()

    def add_action():
        sync_actions()
        try:
            name = simpledialog.askstring('Add action', 'Action ID (lowercase, e.g. steer):', parent=dialog)
        finally:
            dialog.grab_set()
        if not name: return
        name = name.strip().lower()
        if not re.fullmatch(r'[a-z][a-z0-9_-]{0,39}', name) or name in draft['hotkeys'] or len(draft['hotkeys']) >= 12:
            status.set('Use a new lowercase ID; at most 12 actions.'); return
        draft['hotkeys'][name] = free_key()
        render()

    def app_editor(mode):
        sync_actions()
        selection = app_list.curselection()
        source_id = list(draft['apps'])[selection[0]] if selection else None
        if mode != 'add' and source_id is None: return
        app = copy.deepcopy(draft['apps'][source_id]) if mode != 'add' else {
            'name':'New app','selector':'','processes':['app.exe'],'package':'','title_mode':'any','title':'','shortcuts':{}}
        app_id = source_id if mode == 'edit' else next(f'app{n}' for n in range(1,100) if f'app{n}' not in draft['apps'])
        if mode != 'edit': app['selector'] = free_key()
        form = tk.Toplevel(dialog)
        form.title('Edit app' if mode == 'edit' else 'Add app or window')
        form.transient(dialog)
        form.grab_set()
        frame = ttk.Frame(form, padding=14)
        frame.pack(fill='both', expand=True)
        variables = {}
        values = {'id':app_id, 'name':app['name'], 'selector':app['selector'],
                  'processes':', '.join(app['processes']), 'package':app['package'],
                  'title_mode':app['title_mode'], 'title':app['title']}
        choices = {'selector':['']+[f'F{n}' for n in range(13,25)], 'title_mode':['any','app','exact','contains','suffix']}
        labels = {'id':'Unique ID','name':'Display name','selector':'Selector input key','processes':'Executable names (comma separated)',
                  'package':'Package family (optional)','title_mode':'Window title match','title':'Window title pattern'}
        for row, (name, value) in enumerate(values.items()):
            ttk.Label(frame, text=labels[name]).grid(row=row, column=0, sticky='w', pady=4)
            variables[name] = tk.StringVar(value=value)
            if name in choices:
                widget = ttk.Combobox(frame, textvariable=variables[name], values=choices[name], state='readonly', width=44)
            else:
                widget = ttk.Entry(frame, textvariable=variables[name], width=47)
            widget.grid(row=row, column=1, padx=8, sticky='ew')
            if name == 'id' and mode == 'edit': widget.configure(state='readonly')
        windows = get_windows()
        pick = ttk.Combobox(frame, state='readonly', width=68, values=[f'{w[1]} — {w[2]}' for w in windows])
        pick.grid(row=7, column=0, columnspan=2, sticky='ew', pady=6)
        def use_window():
            index = pick.current()
            if index < 0: return
            window = windows[index]
            variables['processes'].set(window[1])
            variables['package'].set(window[3] if len(window) > 3 and window[3] else '')
            variables['title_mode'].set('exact')
            variables['title'].set(window[2])
        ttk.Button(frame, text='Use selected window', command=use_window).grid(row=8, column=1, sticky='w', padx=8)
        shortcut_vars = {}
        for row, name in enumerate(draft['hotkeys'], start=9):
            ttk.Label(frame, text=f'{name} shortcut').grid(row=row, column=0, sticky='w', pady=4)
            shortcut_vars[name] = tk.StringVar(value=app['shortcuts'].get(name,''))
            ttk.Entry(frame, textvariable=shortcut_vars[name], width=47).grid(row=row, column=1, padx=8, sticky='ew')
        error = tk.StringVar()
        ttk.Label(frame, textvariable=error, wraplength=620).grid(row=22, column=0, columnspan=2)
        def accept():
            candidate = copy.deepcopy(draft)
            name = variables['id'].get().strip()
            if mode != 'edit' and name in candidate['apps']:
                error.set('That ID already exists.'); return
            candidate['apps'][name] = {k:v.get().strip() for k,v in variables.items() if k not in ('id','processes')}
            candidate['apps'][name]['processes'] = [p.strip().lower() for p in variables['processes'].get().split(',')]
            candidate['apps'][name]['shortcuts'] = {a:v.get().strip() for a,v in shortcut_vars.items()}
            try: validate_config(candidate)
            except ValueError as problem: error.set(str(problem)); return
            draft['apps'] = candidate['apps']
            form.destroy(); dialog.grab_set(); render()
        ttk.Button(frame, text='Keep changes', command=accept).grid(row=23, column=1, sticky='e', pady=10)
        form.protocol('WM_DELETE_WINDOW', lambda: (form.destroy(), dialog.grab_set()))

    def remove_app():
        sync_actions()
        selected = app_list.curselection()
        if selected and len(draft['apps']) > 1:
            draft['apps'].pop(list(draft['apps'])[selected[0]]); render()
        else: status.set('Keep at least one app.')
    buttons = ttk.Frame(apps_tab)
    buttons.pack(fill='x', padx=10, pady=10)
    for text, command in [('Add app',lambda:app_editor('add')),('Edit',lambda:app_editor('edit')),('Duplicate window',lambda:app_editor('duplicate')),('Remove',remove_app)]:
        ttk.Button(buttons, text=text, command=command).pack(side='left', padx=3)
    ttk.Button(keys_tab, text='Add action', command=add_action).pack(anchor='w', padx=10, pady=10)
    def finish():
        sync_actions()
        try: apply(validate_config(draft))
        except (ValueError,OSError) as problem: status.set(str(problem)); return
        dialog.destroy()
    ttk.Button(dialog, text='Apply and close', command=finish).pack(side='right', padx=12, pady=12)
    ttk.Button(dialog, text='Cancel', command=dialog.destroy).pack(side='right', pady=12)
    render()
    parent.wait_window(dialog)
