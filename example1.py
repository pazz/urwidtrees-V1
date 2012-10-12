#!/usr/bin/python

import urwid
from trees import SimpleTreeWalker


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
for i in range(10):
    subtree = (FocusableText('parent %d' % i), [])
    for j in range(5):
        leaf = (FocusableText('child %d.%d' % (i, j)), None)
        subtree[1].append(leaf)
    tree[1].append(subtree)

# define a list of trees to be passed on to SimpleTreeWalker
forrest = [tree]

if __name__ == "__main__":
    S = SimpleTreeWalker(forrest)  # get a Walker
    treebox = urwid.ListBox(S)  # stick it into a ListBox
    urwid.MainLoop(treebox, palette).run()  # go
