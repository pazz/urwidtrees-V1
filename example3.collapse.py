#!/usr/bin/python
# Copyright (C) 2012  Patrick Totzke <patricktotzke@gmail.com>
# This file is released under the GNU LGPL, version 2.1 or a later revision.

from example1 import swalker, palette  # example data
from widgets import CollapsibleIndentedTreeListWalker  # for Decoration
from widgets import TreeBox
import urwid

if __name__ == "__main__":
    # We ue want subtrees to be collapsible and
    # use Indentation with collapse-icons for decoration.
    # per default we want all grandchildren collapsed.
    if_grandchild = lambda pos: swalker.depth(pos) > 1

    walker = CollapsibleIndentedTreeListWalker(swalker,
                                               is_collapsed=if_grandchild,
                                               #indent=6,
                                               #childbar_offset=1,
                                               selectable_icons=True,
                                               icon_focussed_att='focus',
                                               #icon_frame_left_char=None,
                                               #icon_frame_right_char=None,
                                               #icon_expanded_char='-',
                                               #icon_collapsed_char='+',
                                               )

    # put the walker into a treebox
    treebox = TreeBox(walker)

    rootwidget = urwid.AttrMap(treebox, 'body')
    urwid.MainLoop(rootwidget, palette).run()  # go
