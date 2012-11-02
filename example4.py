#!/usr/bin/python

from example1 import swalker, palette  # example data
from widgets import CollapsibleIndentedTreeListWalker  # for Decoration
from widgets import TreeBox
import urwid

if __name__ == "__main__":
    # add some decoration
    walker = CollapsibleIndentedTreeListWalker(swalker,
                                               indent=0,
                                               icon_offset=1,
                                               #selectable_icons=True,
                                               icon_focussed_att='focus',)

    # put the walker into a treebox
    treebox = TreeBox(walker)

    rootwidget = urwid.AttrMap(treebox, 'body')
    urwid.MainLoop(rootwidget, palette).run()  # go
