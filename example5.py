#!/usr/bin/python

from example1 import swalker, palette  # example data
from widgets import CollapsibleArrowTreeListWalker  # for Decoration
from widgets import TreeBox
import urwid

if __name__ == "__main__":
    # add some decoration
    walker = CollapsibleArrowTreeListWalker(swalker indent=6,
                                            is_collapsed=lambda pos: len(pos) >
                                            3, #icon_offset=1,
                                            childbar_offset=0,
                                            selectable_icons=True,
                                            icon_focussed_att='focus',
                                            #icon_frame_left_char=None,
                                            #icon_frame_right_char=None,
                                            #icon_expanded_char='+',
                                            #icon_collapsed_char='-',
                                            #arrow_tip_char=None,)
                                            )

    # put the walker into a treebox
    treebox = TreeBox(walker)

    rootwidget = urwid.AttrMap(treebox, 'body')
    urwid.MainLoop(rootwidget, palette).run()  # go
