#!/usr/bin/env python3
import gi, re, os, sys
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import subprocess
import time

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------
COLORS_FILE = os.path.join(os.path.dirname(__file__), 'system-menu.colors')

FALLBACK = {
    'bg0':    '#24283b', 'bg1':    '#282d42', 'bg4':    '#3a405e',
    'fg':     '#a9b1d6', 'red':    '#F7768E', 'orange': '#FF9E64',
    'yellow': '#E0AF68', 'green':  '#9ECE6A', 'blue':   '#7AA2F7',
    'purple': '#ad8ee6', 'grey':   '#453B6A',
}

def load_colors(path):
    colors = dict(FALLBACK)
    try:
        with open(path) as f:
            for line in f:
                m = re.match(r'\s*(\w+)\s*=\s*(#[0-9A-Fa-f]{6,8})', line)
                if m:
                    colors[m.group(1)] = m.group(2)
    except FileNotFoundError:
        print(f'[system-menu] {path} not found, using fallback colors.', file=sys.stderr)
    return colors

C = load_colors(COLORS_FILE)

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
CSS = f"""
window {{
    background-color: {C['bg0']};
    border: 1px solid {C['bg4']};
    border-radius: 0px;
}}
#title {{
    color: {C['fg']};
    font-size: 15px;
    font-weight: bold;
    margin-bottom: 4px;
}}
#hint {{
    color: {C['fg']};
    font-size: 11px;
    margin-bottom: 8px;
}}
button {{
    background: {C['bg1']};
    color: {C['fg']};
    border: 1px solid {C['bg4']};
    border-radius: 6px;
    padding: 10px 16px;
    font-size: 12px;
    transition: all 120ms ease;
}}
button:hover  {{ border-color: {C['fg']}; background: {C['bg4']}; }}
button:active {{ background: {C['bg0']}; }}

#btn-lock     {{ color: {C['blue']};   border-color: {C['blue']};   }}
#btn-suspend  {{ color: {C['blue']}; border-color: {C['blue']}; }}
#btn-exit     {{ color: {C['orange']}; border-color: {C['orange']}; }}
#btn-reboot   {{ color: {C['orange']}; border-color: {C['orange']}; }}
#btn-shutdown {{ color: {C['red']};    border-color: {C['red']};    }}

#btn-lock:hover     {{ background: alpha({C['blue']},   0.15); }}
#btn-suspend:hover  {{ background: alpha({C['blue']}, 0.15); }}
#btn-exit:hover     {{ background: alpha({C['orange']}, 0.15); }}
#btn-reboot:hover   {{ background: alpha({C['orange']}, 0.15); }}
#btn-shutdown:hover {{ background: alpha({C['red']},    0.15); }}
"""

provider = Gtk.CssProvider()
provider.load_from_data(CSS.encode())
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------
def run(cmd):
    subprocess.Popen(cmd, shell=True)
    Gtk.main_quit()

def on_key(_widget, event):
    match Gdk.keyval_name(event.keyval):
        case 'l':
            run('swaylock --screenshots --effect-blur 7x5 --fade-in 0.2')
        case 'e':
            run('swaymsg exit')
        case 's':
            run('systemctl suspend')
        case 'R':
            run('systemctl reboot')
        case 'S':
            run('systemctl poweroff')
        case 'Escape' | 'Return':
            Gtk.main_quit()

# ---------------------------------------------------------------------------
# Window
# ---------------------------------------------------------------------------
win = Gtk.Window(title='System')
win.set_border_width(24)
win.set_position(Gtk.WindowPosition.CENTER)
win.set_keep_above(True)
win.set_resizable(False)
win.set_decorated(False)
win.connect('destroy', Gtk.main_quit)
win.connect('key-press-event', on_key)

vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
win.add(vbox)

title = Gtk.Label(label='System')
title.set_name('title')
vbox.pack_start(title, False, False, 0)

hint = Gtk.Label(label='Esc to cancel')
hint.set_name('hint')
vbox.pack_start(hint, False, False, 0)

hbox = Gtk.Box(spacing=8)
vbox.pack_start(hbox, False, False, 0)

buttons = [
    ('btn-lock',     '(l)ock',            'swaylock -f -c 000000'),
    ('btn-suspend',  '(s)uspend',         'systemctl suspend'),
    ('btn-exit',     '(e)xit',            'swaymsg exit'),
    ('btn-reboot',   'Shift+(R)eboot',    'systemctl reboot'),
    ('btn-shutdown', 'Shift+(S)hutdown',  'systemctl poweroff'),
]

for widget_id, label, cmd in buttons:
    btn = Gtk.Button(label=label)
    btn.set_name(widget_id)
    btn.connect('clicked', lambda _w, c=cmd: run(c))
    hbox.pack_start(btn, True, True, 0)

win.show_all()
Gtk.main()
