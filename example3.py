#!/usr/bin/python
from example1 import swalker, palette  # example data
from widgets import ArrowTreeListWalker  # for Decoration
from widgets import TreeBox
import urwid

if __name__ == "__main__":
    # add some decoration
    walker = ArrowTreeListWalker(swalker)

    # put the walker into a treebox
    treebox = TreeBox(walker)

    rootwidget = urwid.AttrMap(treebox,'body')
    urwid.MainLoop(rootwidget, palette).run()  # go


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

