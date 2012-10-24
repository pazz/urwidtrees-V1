from urwid import signals
#import logging


class TreeWalker(object):
    """
    Content provider for tree structures. Base class for a structured walk
    over acyclic graphs that can be displayed by :class:`TreeBox` widgets.

    Subclasses may implement methods
     * `next_sibbling_position`
     * `prev_sibbling_position`
     * `parent_position`
     * `first_child_position`
     * `last_child_position`

     that compute the next position in the respective direction. Also, they
     need to implement method `__getitem__` that returns a widget for a given position.
    """
    __metaclass__ = signals.MetaSignals
    signals = ["modified"]
    focus = None

    def _modified(self):
        signals.emit_signal(self, "modified")

    def _get(self, pos):
        """loads widget at given position; handling invalid arguments"""
        res = None, None
        if pos is not None:
            try:
                res = self[pos], pos
            except (IndexError, KeyError):
                pass
        return res

    def get_focus(self):
        """return focussed widget."""
        return self._get(self.focus)

    def set_focus(self, pos):
        """set focus to widget at given pos."""
        self.focus = pos
        #self._modified()

# To be overwritten by subclasses
    def parent_position(self, pos):
        return None

    def first_child_position(self, pos):
        return None

    def last_child_position(self, pos):
        return None

    def next_sibbling_position(self, pos):
        return None

    def prev_sibbling_position(self, pos):
        return None
# end of TreeWalker


class LazyTreeWalker(TreeWalker):
    """TreeWalker that caches its contained widgets"""
    def __init__(self, load_widget):
        """
        :param load_widget: a callable that returns a Widget for given position
        """
        TreeWalker.__init__(self)
        self._content = {}
        self._load_widget = load_widget

    def __getitem__(self, pos):
        if pos not in self._content:
            widget = self._load_widget(pos)
            if widget is None:
                raise IndexError
            self._content[pos] = widget
        return self._content[pos]


class SimpleTreeWalker(TreeWalker):
    """
    Walks on a given fixed acyclic structure.
    The structure needs to be a list of nodes; every node is a tuple `(widget,
    children)`, where widget is a urwir.Widget to be displayed at that position
    and children is either None or a list of nodes.

    positions are lists of ints determining a path from toplevel node.
    """
    def __init__(self, treelist):
        self.focus = (0,)
        self._treelist = treelist
        TreeWalker.__init__(self)

    def _get_subtree(self, treelist, path):
        """recursive helper to look up node-tuple for `path` in `treelist`"""
        subtree = None
        if len(path) > 1:
            subtree = self._get_subtree(treelist[path[0]][1], path[1:])
        else:
            try:
                subtree = treelist[path[0]]
            except (IndexError, TypeError):
                pass
        return subtree

    def _get_node(self, treelist, path):
        """look up widget at `path` of `treelist`; default to None if nonexistent."""
        node = None
        if path is not None:
            subtree = self._get_subtree(treelist, path)
            if subtree is not None:
                node = subtree[0]
        return node

    def __getitem__(self, pos):
        return self._get_node(self._treelist, pos)

    def parent_position(self, pos):
        parent = None
        if pos is not None:
            if len(pos) > 1:
                parent = pos[:-1]
        return parent

    def _confirm_pos(self, pos):
        candidate = None
        if self._get_node(self._treelist, pos) is not None:
            candidate = pos
        return candidate

    def first_child_position(self, pos):
        return self._confirm_pos(pos + (0,))

    def last_child_position(self, pos):
        candidate = None
        subtree = self._get_subtree(self._treelist, pos)
        children = subtree[1]
        if children is not None:
            candidate = pos + (len(children) - 1,)
        return candidate

    def next_sibbling_position(self, pos):
        return self._confirm_pos(pos[:-1] + (pos[-1] + 1,))

    def prev_sibbling_position(self, pos):
        return pos[:-1] + (pos[-1] - 1,) if (pos[-1] > 0) else None
