#!/usr/bin/python

import logging
import urwid
from walkers import SimpleTreeWalker
from widgets import TreeBox


class FocusableText(urwid.WidgetWrap):
    def __init__(self, txt):
        t = urwid.Text(txt)
        w = urwid.AttrMap(t, 'body', 'focus')
        urwid.WidgetWrap.__init__(self, w)

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key

# define some nice colours
palette = [
    ('body', 'black', 'light gray'),
    ('focus', 'light gray', 'dark blue', 'standout'),
    ('bars', 'dark red', 'light gray', ''),
    ('arrowtip', 'light red', 'light gray', ''),
]

# define a test tree
tree = (FocusableText('root'), [])
for i in range(5):
    subtree = (FocusableText('parent %d' % i), [])
    for j in range(5):
        leaf = (FocusableText('child %d.%d' % (i, j)), None)
        subtree[1].append(leaf)
    tree[1].append(subtree)

# define a list of trees to be passed on to SimpleTreeWalker
forrest = [tree]

if __name__ == "__main__":
    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    S = SimpleTreeWalker(forrest)  # get a Walker
    treebox = TreeBox(S,
                      indent=3,
                      # double
                      # arrow_hbar=u'\u2550',
                      # arrow_vbar=u'\u2551',
                      # arrow_tip=u'\u25b6',
                      # arrow_connector_t=u'\u2560',
                      # arrow_connector_l=u'\u255a',
                      #thin
                      arrow_hbar_char=u'\u2500',
                      arrow_hbar_att='bars',
                      arrow_vbar_char=u'\u2502',
                      arrow_vbar_att='bars',
                      arrow_tip_char=u'\u27a4',
                      arrow_tip_att='arrowtip',
                      void_att='bars',
                      # arrow_connector_t=u'\u251c',
                      # arrow_connector_l=u'\u2514', # u'\u2570' # round
                      #thick
                      #arrow_hbar_char=u'\u2501',
                      #arrow_hbar_att='highlight',
                      # arrow_vbar=u'\u2503',
                      # arrow_tip=u'\u25b6',
                      # arrow_connector_t=u'\u2523',
                      # arrow_connector_l=u'\u2517'
                      )  # stick it into a ListBox
    urwid.MainLoop(treebox, palette).run()  # go
