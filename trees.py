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
        """return focussed widget. Needed by ListBox!"""
        return self._get(self.focus)

    def set_focus(self, pos):
        """set focus to widget at given pos. Needed by ListBox!"""
        self.focus = pos
        self._modified()

    def get_next(self, pos):
        """
        get next widget after given position in depth-first order.
        Needed by ListBox!
        """
        return self._get(self.next_position(pos))

    def get_prev(self, pos):
        """
        get previous widget after given position in depth-first order.
        Needed by ListBox!
        """
        return self._get(self.prev_position(pos))

# Getter for widgets in various directions. IMHO this clutters the API
# and TreeBox widgets shoud rather directly use the position-getter
# in combination with __getitem__.
#
#    def get_next_sibbling(self, pos):
#        return self._get(self.next_sibbling_position(pos))
#
#    def get_prev_sibbling(self, pos):
#        return self._get(self.prev_sibbling_position(pos))
#
#    def get_parent(self, pos):
#        return self._get(self.parent_position(pos))
#
#    def get_first_child(self, pos):
#        return self._get(self.first_child_position(pos))
#
#    def get_last_child(self, pos):
#        return self._get(self.last_child_position(pos))

    def _next_of_kin(self, pos):
        """
        Looks up the next sibbling of the closest ancestor with next sibblings.
        This helper is used later to compute next_position in DF-order.
        """
        candidate = None
        parent = self.parent_position(pos)
        if parent is not None:
            candidate = self.next_sibbling_position(parent)
            if candidate is None:
                candidate = self._next_of_kin(parent)
        return candidate

    def next_position(self, pos):
        """returns the next position in depth-first order"""
        candidate = self.first_child_position(pos)
        if candidate is None:
            candidate = self.next_sibbling_position(pos)
            if candidate is None:
                candidate = self._next_of_kin(pos)
        return candidate

    def _last_decendant_position(self, pos):
        """
        Looks up the last node in DF-order in the subtree starting a pos.
        This helper is used later to compute prev_position in DF-order.
        """
        candidate = pos
        last_child = self.last_child_position(pos)
        if last_child is not None:
            candidate = self._last_decendant_position(last_child)
        return candidate

    def prev_position(self, pos):
        """returns the previous position in depth-first order"""
        candidate = None
        prevsib = self.prev_sibbling_position(pos)  # is None if first
        if prevsib is not None:
            candidate = self._last_decendant_position(prevsib)
        else:
            parent = self.parent_position(pos)
            if parent is not None:
                candidate = parent
        return candidate

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
        self.focus = [0]
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
        subtree = self._get_subtree(treelist, path)
        if subtree is not None:
            node = subtree[0]
        return node

    def __getitem__(self, pos):
        return self._get_node(self._treelist, pos)

    def parent_position(self, pos):
        parent = None
        if len(pos) > 1:
            parent = pos[:-1]
        return parent

    def _confirm_pos(self, pos):
        candidate = None
        if self._get_node(self._treelist, pos) is not None:
            candidate = pos
        return candidate

    def first_child_position(self, pos):
        return self._confirm_pos(pos + [0])

    def last_child_position(self, pos):
        candidate = None
        subtree = self._get_subtree(self._treelist, pos)
        children = subtree[1]
        if children is not None:
            candidate = pos + [len(children) - 1]
        return candidate

    def next_sibbling_position(self, pos):
        return self._confirm_pos(pos[:-1] + [pos[-1] + 1])

    def prev_sibbling_position(self, pos):
        return pos[:-1] + [pos[-1] - 1] if (pos[-1] > 0) else None
