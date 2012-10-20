#!/usr/bin/python

import logging
import urwid
from walkers import SimpleTreeWalker
from widgets import TreeBox
from widgets import CollapsibleListWalkerAdapter


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
    ('bars', 'dark blue', 'light gray', ''),
    ('arrowtip', 'light blue', 'light gray', ''),
    ('connectors', 'light red', 'light gray', ''),
]

# define a test tree
tree = (FocusableText('ROOT (0,)'), [])
for i in range(5):
    subtree = (FocusableText('NODE(0,%d)' % i), [])
    for j in range(2):
        subsubtree = (FocusableText('NODE (0.%d.%d)' % (i, j)), [])
        for k in range(3):
            leaf = (FocusableText('LEAF (0.%d.%d.%d)' % (i, j, k)), None)
            subsubtree[1].append(leaf)
        subtree[1].append(subsubtree)
    tree[1].append(subtree)

# define a list of trees to be passed on to SimpleTreeWalker
forrest = [tree]

if __name__ == "__main__":
    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    treebox = TreeBox(SimpleTreeWalker(forrest),        # get a Walker
                      # decoration_adapter=None,        # turn off decoration
                      decoration_adapter=CollapsibleListWalkerAdapter,
                      selectable_icons=True,
                      ## remaining keywords are passed to the decoration_adapter
                      indent=3,                         # indentation between levels
                      icon_expanded_char=u'\u2295',
                      icon_collapsed_char=u'\u2297',
                      icon_focussed_att='focus',
                      ## double bars
                      # arrow_hbar=u'\u2550',
                      # arrow_vbar=u'\u2551',
                      # arrow_tip=u'\u25b6',
                      # arrow_connector_t=u'\u2560',
                      # arrow_connector_l=u'\u255a',
                      # thin bars
                      #arrow_hbar_char=u'\u2500',
                      arrow_att='bars',
                      #arrow_hbar_att='bars',
                      #arrow_vbar_char=u'\u2502',
                      #arrow_vbar_char=None,
                      #arrow_vbar_att='bars',
                      arrow_tip_char=u'\u27a4',
                      arrow_tip_att='arrowtip',
                      #arrow_connector_att='connectors',
                      #arrow_connector_tchar=None,
                      #arrow_connector_lchar=None,
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
