#!/usr/bin/python

from example1 import swalker, palette  # example data
from widgets import CollapsibleArrowTreeListWalker  # for Decoration
from widgets import TreeBox
from walkers import SimpleTreeWalker
import urwid

if __name__ == "__main__":
    # add some decoration
    first = CollapsibleArrowTreeListWalker(swalker, indent=4,
                            # thin bars
                            arrow_hbar_char=u'\u2500',
                            arrow_hbar_att='bars',
                            arrow_vbar_char=u'\u2502',
                            arrow_vbar_att='bars',
                            )
    second = CollapsibleArrowTreeListWalker(swalker, indent=4,
                            # double bars
                            arrow_hbar_char=u'\u2550',
                            arrow_vbar_char=u'\u2551',
                            arrow_tip_char=u'\u25b6',
                            arrow_connector_tchar=u'\u2560',
                            arrow_connector_lchar=u'\u255a',
                            )


    outerwalker = SimpleTreeWalker([
        (TreeBox(first), []),
    #    (TreeBox(second), [])
    ])

    # put the walker into a treebox
    treebox = TreeBox(outerwalker)

    treebox = urwid.ListBox([urwid.ListBox([urwid.Text('Hi')]) ])

    rootwidget = urwid.AttrMap(treebox, 'body')
    urwid.MainLoop(rootwidget, palette).run()  # go

    I = IndentedTreeListWalker(S, indent=5)
    C = CollapsibleTreeListWalker(S)
    CI = CollapsibleIndentedTreeListWalker(S, indent=2, icon_offset=1,
                                           selectable_icons=True,
                                           icon_focussed_att='focus',
                                           )
