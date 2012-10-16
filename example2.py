#!/usr/bin/python

import urwid
import os
from walkers import LazyTreeWalker
from widgets import TreeBox


class FocusableText(urwid.WidgetWrap):
    def __init__(self, txt):
        t = urwid.Text(txt)
        w = urwid.AttrMap(t, 'body', 'focus')
        urwid.WidgetWrap.__init__(self, w)

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key


class DirectoryWalker(LazyTreeWalker):
    def __init__(self, pwd):
        self.focus = pwd
        self.dirsep = getattr(os.path, 'sep', '/')  # separator for this os
        LazyTreeWalker.__init__(self, self.load_widget)

    def load_widget(self, pos):
        return FocusableText(pos)

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


# define some nice colours
palette = [
    ('body', 'black', 'light gray'),
    ('focus', 'light gray', 'dark blue', 'standout'),
]


if __name__ == "__main__":
    cwd = os.getcwd()  # get current working directory
    D = DirectoryWalker(cwd)  # get a Walker with cwd as initial focus
    treebox = TreeBox(D, indent=4)  # stick it into a TreeBox
    #treebox = urwid.ListBox(D)  # stick it into a ListBox
    urwid.MainLoop(treebox, palette).run()  # go
