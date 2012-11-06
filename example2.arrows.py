#!/usr/bin/python
# Copyright (C) 2012  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU LGPL, version 2.1 or a later revision.

from example1 import swalker, palette  # example data
from widgets import ArrowTreeListWalker  # for Decoration
from widgets import TreeBox
import urwid

if __name__ == "__main__":
    # add some decoration.
    # we use the defauts for this decorator. Note that ArrowTreeListWalker
    # allows many customizations via constructor parameters..
    walker = ArrowTreeListWalker(swalker)

    # put the walker into a treebox
    treebox = TreeBox(walker)

    rootwidget = urwid.AttrMap(treebox, 'body')
    urwid.MainLoop(rootwidget, palette).run()  # go
