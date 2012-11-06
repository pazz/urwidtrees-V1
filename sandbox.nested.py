#!/usr/bin/python

from example1 import swalker, palette, construct_example_tree  # example data
from widgets import ArrowTreeListWalker,TreeListWalker, IndentedTreeListWalker, TreeBox
from walkers import SimpleTreeWalker, NestedTreeWalker
import urwid
from urwid import WidgetWrap, Pile
import logging





if __name__ == "__main__":
    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    # add some decoration.
    # we use the defauts for this decorator. Note that ArrowTreeListWalker
    # allows many customizations via constructor parameters..
    awalker = ArrowTreeListWalker(swalker)
    tree = construct_example_tree()
    tree[1][0][1].append((awalker, None))
    swalker = IndentedTreeListWalker(NestedTreeWalker(SimpleTreeWalker([tree])))

    # put the walker into a treebox
    treebox = TreeBox(swalker)
    rootwidget = urwid.AttrMap(treebox, 'body')
    urwid.MainLoop(rootwidget, palette).run()  # go
