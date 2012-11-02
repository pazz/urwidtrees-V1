#!/usr/bin/python

import logging
import urwid
from walkers import SimpleTreeWalker
from widgets import TreeBox


# define some colours
palette = [
    ('body', 'black', 'light gray'),
    ('focus', 'light gray', 'dark blue', 'standout'),
    ('bars', 'dark blue', 'light gray', ''),
    ('arrowtip', 'light blue', 'light gray', ''),
    ('connectors', 'light red', 'light gray', ''),
]

# define a test tree in the format accepted by
# SimpleTreeWalker. Essentially, a tree is given as
# (nodewidget, [list, of, subtrees]). SimpleTreeWalker
# accepts lists of such trees.
def construct_example_tree(selectable_nodes=True):

    class FocusableText(urwid.WidgetWrap):
        """Selectable Text used for nodes in our example"""
        def __init__(self, txt):
            t = urwid.Text(txt)
            w = urwid.AttrMap(t, 'body', 'focus')
            urwid.WidgetWrap.__init__(self, w)

        def selectable(self):
            return selectable_nodes

        def keypress(self, size, key):
            return key

    # define root node
    tree = (FocusableText('ROOT (0,)'), [])

    # define some children
    for i in range(5):
        subtree = (FocusableText('NODE(0,%d)' % i), [])
        # and grandchildren..
        for j in range(2):
            subsubtree = (FocusableText('NODE (0.%d.%d)' % (i, j)), [])
            for k in range(3):
                leaf = (FocusableText('LEAF (0.%d.%d.%d)' % (i, j, k)), None)
                subsubtree[1].append(leaf)
            subtree[1].append(subsubtree)
        tree[1].append(subtree)
    return tree

# define a list of trees to be passed on to SimpleTreeWalker
forrest = [construct_example_tree()]

# stick out test tree into a SimpleTreeWalker
swalker = SimpleTreeWalker(forrest)

if __name__ == "__main__":
    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    # put the walker into a treebox
    treebox = TreeBox(swalker)

    # add some decoration
    rootwidget = urwid.AttrMap(treebox,'body')
    urwid.MainLoop(rootwidget, palette).run()  # go
