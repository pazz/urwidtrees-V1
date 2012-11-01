#!/usr/bin/python

import logging
import urwid
from walkers import SimpleTreeWalker
from widgets import TreeBox, TreeListWalker
from widgets import IndentedTreeListWalker
from widgets import ArrowTreeListWalker
from widgets import CollapsibleArrowTreeListWalker
from widgets import CollapsibleIndentedTreeListWalker
from widgets import CollapsibleTreeListWalker


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
    S = SimpleTreeWalker(forrest)
    I = IndentedTreeListWalker(S, indent=5)
    C = CollapsibleTreeListWalker(S)
    CI = CollapsibleIndentedTreeListWalker(S, indent=2, icon_offset=1,
                                        selectable_icons=True,
                                        icon_focussed_att='focus',
                                          )
    CA = CollapsibleArrowTreeListWalker(S, indent=6, is_collapsed=lambda pos: len(pos)>3,
                                        #icon_offset=1,
                                        childbar_offset=0,
                                        selectable_icons=True,
                                        icon_focussed_att='focus',
                                        #icon_frame_left_char=None,
                                        #icon_frame_right_char=None,
                                        #icon_expanded_char='+',
                                        #icon_collapsed_char='-',
                                        #arrow_tip_char=None,
                                       )
    A = ArrowTreeListWalker(S, indent=4,
                            #indent_att='body',
                            #childbar_offset=1,
                            #arrow_hbar_char=u'\u2550',
                            #arrow_vbar_char=u'\u2551',
                            #arrow_tip_char=None,#u'\u25b6',
                            #arrow_connector_tchar=u'\u2560',
                            #arrow_connector_lchar=u'\u255a',)

                      ### double bars
                      ## arrow_hbar=u'\u2550',
                      ## arrow_vbar=u'\u2551',
                      ## arrow_tip=u'\u25b6',
                      ## arrow_connector_t=u'\u2560',
                      ## arrow_connector_l=u'\u255a',

                      ## thin bars
                      ##arrow_hbar_char=u'\u2500',
                      #arrow_att='bars',
                      ##arrow_hbar_att='bars',
                      ##arrow_vbar_char=u'\u2502',
                      ##arrow_vbar_char=None,
                      ##arrow_vbar_att='bars',
                      #arrow_tip_char='>>',  # =u'\u27a4',
                      #arrow_tip_att='arrowtip',
                      ##arrow_connector_att='connectors',
                      ##arrow_connector_tchar='TT',
                      ##arrow_connector_lchar=None,
                      ## arrow_connector_t=u'\u251c',
                      ## arrow_connector_l=u'\u2514', # u'\u2570' # round
                      ##thick
                      ##arrow_hbar_char=u'\u2501',
                      ##arrow_hbar_att='highlight',
                      ## arrow_vbar=u'\u2503',
                      ## arrow_tip=u'\u25b6',
                      ## arrow_connector_t=u'\u2523',
                      ## arrow_connector_l=u'\u2517'
                           )

    T = urwid.AttrMap(TreeBox(CI, focus=(0,)),'body')
    #T = urwid.AttrMap(urwid.ListBox(CI),'body')
    urwid.MainLoop(T, palette).run()  # go
