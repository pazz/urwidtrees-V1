#!/usr/bin/python

from example1 import swalker, palette, construct_example_tree  # example data
from widgets import ArrowTreeListWalker,TreeListWalker, IndentedTreeListWalker,TreeBox
from walkers import SimpleTreeWalker
import urwid
from urwid import WidgetWrap, Pile
import logging

class TreePile(WidgetWrap):
    _selectable = True

    def __init__(self, walker, **kwargs):
        if not isinstance(walker, TreeListWalker):
            walker = TreeListWalker(walker)
        self._walker = walker
        self._lines = []
        self.loadlines()
        logging.debug('lines:\n\n%s' % str(self._lines))
        self._pile = Pile(self._lines)
        self.__super.__init__(self._pile)

    def loadlines(self):
        widget, pos = self._walker.get_focus()
        while pos is not None:
            self._lines.append(widget)
            widget, pos = self._walker.get_next(pos)

    # Widget API
    def get_focus(self):
        return self._pile.get_focus()

    def keypress(self, size, key):
        key = self._pile.keypress(size, key)
        if key in ['left', 'right', '[', ']', '-', '+', 'C', 'E']:
            if key == 'left':
                self.focus_parent()
            elif key == 'right':
                self.focus_first_child()
            elif key == '[':
                self.focus_prev_sibling()
            elif key == ']':
                self.focus_next_sibling()
            if isinstance(self._walker, CollapseMixin):
                if key == '-':
                    w, focuspos = self._walker.get_focus()
                    self._walker.collapse(focuspos)
                elif key == '+':
                    w, focuspos = self._walker.get_focus()
                    self._walker.expand(focuspos)
                elif key == 'C':
                    self._walker.collapse_all()
                elif key == 'E':
                    self._walker.expand_all()
            # This is a hack around ListBox misbehaving:
            # it seems impossible to set the focus without calling keypress as
            # otherwise the change becomes visible only after the next render()
            return self._pile.keypress(size, None)
        else:
            return self._pile.keypress(size, key)

    # Tree based focus movement
    def focus_parent(self):
        w, focuspos = self._walker.get_focus()
        parent = self._walker.parent_position(focuspos)
        if parent is not None:
            self._pile.set_focus(parent)

    def focus_first_child(self):
        w, focuspos = self._walker.get_focus()
        child = self._walker.first_child_position(focuspos)
        if child is not None:
            self._outer_list.set_focus(child)

    def focus_next_sibling(self):
        w, focuspos = self._walker.get_focus()
        sib = self._walker.next_sibling_position(focuspos)
        if sib is not None:
            self._outer_list.set_focus(sib)

    def focus_prev_sibling(self):
        w, focuspos = self._walker.get_focus()
        sib = self._walker.prev_sibling_position(focuspos)
        if sib is not None:
            self._outer_list.set_focus(sib)



if __name__ == "__main__":
    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    # add some decoration.
    # we use the defauts for this decorator. Note that ArrowTreeListWalker
    # allows many customizations via constructor parameters..
    walker = ArrowTreeListWalker(swalker)

    innertree = TreePile(walker)
    tree = construct_example_tree()
    tree[1].append((innertree,[]))

    # put the walker into a treebox
    treebox = TreeBox(IndentedTreeListWalker(SimpleTreeWalker([tree])))
    rootwidget = urwid.AttrMap(treebox, 'body')
    urwid.MainLoop(rootwidget, palette).run()  # go
