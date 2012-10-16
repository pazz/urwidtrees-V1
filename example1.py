#!/usr/bin/python

import logging
import urwid
from trees import SimpleTreeWalker
from widget import TreeBox


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
                      arrow_hbar=u'\u2500',
                      arrow_vbar=u'\u2502',
                      arrow_tip=u'\u25b6',
                      arrow_connector_t=u'\u251c',
                      arrow_connector_l=u'\u2514'
                      )  # stick it into a ListBox
    urwid.MainLoop(treebox, palette).run()  # go
