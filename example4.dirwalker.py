#!/usr/bin/python

import urwid
import os
from example1 import palette  # example data
from widgets import TreeBox
from walkers import CachingTreeWalker
from widgets import CollapsibleArrowTreeListWalker


class FocusableText(urwid.WidgetWrap):
    """Widget to display paths lines"""
    def __init__(self, txt):
        t = urwid.Text(txt)
        w = urwid.AttrMap(t, 'body', 'focus')
        urwid.WidgetWrap.__init__(self, w)

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key


class DirectoryWalker(CachingTreeWalker):
    """
    A custom TreeWalker representing our filesystem structure.
    We subclass CachingTreeWalker instead of TreeWalker to cache constructed lines..
    """
    # determine dir separator and form of root node
    pathsep = os.path.sep
    drive, _ = os.path.splitdrive(pathsep)

    # define root node This is part of the TreeWalker API!
    root = drive + pathsep

    # initialize and tell Caching superclass how to construct new lines
    def __init__(self):
        CachingTreeWalker.__init__(self, self.load_widget)

    def load_widget(self, pos):
        return FocusableText(pos)

    # generic helper
    def _list_dir(self, path):
        """returns absolute paths for all entries in a directory"""
        try:
            elements = [os.path.join(
                path, x) for x in os.listdir(path) if os.path.isdir(path)]
            elements.sort()
        except OSError:
            elements = None
        return elements

    def _get_sibblings(self, pos):
        """lists the parent directory of pos """
        parent = self.parent_position(pos)
        sibblings = [pos]
        if parent is not None:
            sibblings = self._list_dir(parent)
        return sibblings

    # TreeWalker API
    def parent_position(self, pos):
        parent = None
        if pos != '/':
            parent = os.path.split(pos)[0]
        return parent

    def first_child_position(self, pos):
        candidate = None
        if os.path.isdir(pos):
            children = self._list_dir(pos)
            if children:
                candidate = children[0]
        return candidate

    def last_child_position(self, pos):
        candidate = None
        if os.path.isdir(pos):
            children = self._list_dir(pos)
            if children:
                candidate = children[-1]
        return candidate

    def next_sibbling_position(self, pos):
        candidate = None
        sibblings = self._get_sibblings(pos)
        myindex = sibblings.index(pos)
        if myindex + 1 < len(sibblings):  # pos is not the last entry
            candidate = sibblings[myindex + 1]
        return candidate

    def prev_sibbling_position(self, pos):
        candidate = None
        sibblings = self._get_sibblings(pos)
        myindex = sibblings.index(pos)
        if myindex > 0:  # pos is not the first entry
            candidate = sibblings[myindex - 1]
        return candidate

if __name__ == "__main__":
    cwd = os.getcwd()  # get current working directory
    walker = DirectoryWalker()  # get a directory walker

    # define initial collapse
    as_deep_as_cwd = lambda pos: walker.depth(pos) >= walker.depth(cwd)

    # add arrow decoration.
    # We hide the usual arrow tip and icon frame and use a custom arrow tip to
    # indicate the collapse status.  Collapse icons are kept non-selectable, so
    # use the key bindings +/- to collapse subtrees.
    dwalker = CollapsibleArrowTreeListWalker(walker,
                                             focus=cwd,
                                             # set cwd as initial focus
                                             is_collapsed=as_deep_as_cwd,
                                             arrow_tip_char=None,
                                             icon_frame_left_char=None,
                                             icon_frame_right_char=None,
                                             icon_collapsed_char=u'\u25B6',
                                             icon_expanded_char=u'\u25B7')

    # stick it into a TreeBox and use 'body' color attribute for gaps
    treebox = urwid.AttrMap(TreeBox(dwalker), 'body')
    urwid.MainLoop(treebox, palette).run()  # go
