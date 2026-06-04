#!/usr/bin/env python3
import gi, os, sys
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import subprocess

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
CSS_FILE = os.path.join(os.path.dirname(__file__), 'style.css')

provider = Gtk.CssProvider()
try:
    provider.load_from_path(CSS_FILE)
except Exception as e:
    print(f'[system-menu] Could not load {CSS_FILE}: {e}', file=sys.stderr)

Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------
def run(cmd):
    Gtk.main_quit()
    subprocess.run(cmd, shell=True)


# Handled by swayidle
# LOCK = 'swaylock --screenshots --effect-blur 7x5 --fade-in 0.2'


def on_key(_widget, event):
    match Gdk.keyval_name(event.keyval):
        case 'l': run(LOCK)
        case 'e': run('swaymsg exit')
        case 's': run('systemctl suspend')
        case 'R': run('systemctl reboot')
        case 'S': run('systemctl poweroff')
        case 'Escape' | 'Return': Gtk.main_quit()


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
    ('btn-lock',     '(l)ock',           'swaylock -f -c 000000'),
    ('btn-suspend',  '(s)uspend',        'systemctl suspend'),
    ('btn-exit',     '(e)xit',           'swaymsg exit'),
    ('btn-reboot',   'Shift+(R)eboot',   'systemctl reboot'),
    ('btn-shutdown', 'Shift+(S)hutdown', 'systemctl poweroff'),
]

for widget_id, label, cmd in buttons:
    btn = Gtk.Button(label=label)
    btn.set_name(widget_id)
    btn.connect('clicked', lambda _w, c=cmd: run(c))
    hbox.pack_start(btn, True, True, 0)

win.show_all()
Gtk.main()
