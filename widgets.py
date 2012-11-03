import urwid
from urwid import AttrMap, Text, WidgetWrap, ListBox, Columns, SolidFill
from urwid import signals
import logging


class TreeListWalker(urwid.ListWalker):
    """
    Base class for Decoration adapters:
    Objects of this type wrap a given TreeWalker and turn it into
    a ListWalker compatible with ListBox.
    """
    def __init__(self, treewalker, focus=None, **kwargs):
        self._walker = treewalker
        self._focus = focus or treewalker.root

    def __getitem__(self, pos):
        return self._walker[pos]

    def _get(self, pos):
        """loads widget at given position; handling invalid arguments"""
        res = None, None
        if pos is not None:
            try:
                res = self[pos], pos
            except (IndexError, KeyError):
                pass
        return res

    # List Walker API
    def get_focus(self):
        return self._get(self._focus)

    def set_focus(self, pos):
        self._focus = pos

    def get_next(self, pos):
        return self._get(self.next_position(pos))

    def get_prev(self, pos):
        return self._get(self.prev_position(pos))

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

    def _last_decendant_position(self, pos):
        """Looks up the last node in the subtree starting a pos."""
        candidate = pos
        last_child = self.last_child_position(pos)
        if last_child is not None:
            candidate = self._last_decendant_position(last_child)
        return candidate

    def next_position(self, pos):
        """returns the next position in depth-first order"""
        candidate = None
        if pos is not None:
            candidate = self.first_child_position(pos)
            if candidate is None:
                candidate = self.next_sibbling_position(pos)
                if candidate is None:
                    candidate = self._next_of_kin(pos)
        return candidate

    def prev_position(self, pos):
        """returns the previous position in depth-first order"""
        candidate = None
        if pos is not None:
            prevsib = self.prev_sibbling_position(pos)  # is None if first
            if prevsib is not None:
                candidate = self._last_decendant_position(prevsib)
            else:
                parent = self.parent_position(pos)
                if parent is not None:
                    candidate = parent
        return candidate
    # end of List Walker API

    # Tree Walker API
    def prev_sibbling_position(self, pos):
        return self._walker.prev_sibbling_position(pos)

    def next_sibbling_position(self, pos):
        return self._walker.next_sibbling_position(pos)

    def parent_position(self, pos):
        return self._walker.parent_position(pos)

    def first_child_position(self, pos):
        return self._walker.first_child_position(pos)

    def last_child_position(self, pos):
        return self._walker.last_child_position(pos)
    # end of Tree Walker API


class TreeBox(WidgetWrap):
    """A widget representing something in a nested tree display.
    This is essentially a ListBox with the ability to move the focus
    based on directions in the Tree."""
    _selectable = True

    def __init__(self, walker, **kwargs):
        if not isinstance(walker, TreeListWalker):
            walker = TreeListWalker(walker)
        self._walker = walker
        self._outer_list = ListBox(walker)
        self.__super.__init__(self._outer_list)

    def get_focus(self):
        return self._outer_list.get_focus()

    def focus_parent(self):
        w, focuspos = self._walker.get_focus()
        parent = self._walker.parent_position(focuspos)
        if parent is not None:
            self._outer_list.set_focus(parent)

    def focus_first_child(self):
        w, focuspos = self._walker.get_focus()
        child = self._walker.first_child_position(focuspos)
        if child is not None:
            self._outer_list.set_focus(child)

    def focus_next_sibbling(self):
        w, focuspos = self._walker.get_focus()
        sib = self._walker.next_sibbling_position(focuspos)
        if sib is not None:
            self._outer_list.set_focus(sib)

    def focus_prev_sibbling(self):
        w, focuspos = self._walker.get_focus()
        sib = self._walker.prev_sibbling_position(focuspos)
        if sib is not None:
            self._outer_list.set_focus(sib)

    def keypress(self, size, key):
        """
        TreeBox interprets `left/right` as well as page `up/down` to move the
        focus to parent/first child and next/previous sibbling respectively.
        All other keys are passed to the underlying ListBox.
        """
        key = self._outer_list.keypress(size, key)
        if key in ['left', 'right', '[', ']', '-', '+']:
            if key == 'left':
                self.focus_parent()
            elif key == 'right':
                self.focus_first_child()
            elif key == '[':
                self.focus_prev_sibbling()
            elif key == ']':
                self.focus_next_sibbling()
            if isinstance(self._walker, CollapseMixin):
                if key == '-':
                    w, focuspos = self._walker.get_focus()
                    self._walker.collapse(focuspos)
                elif key == '+':
                    w, focuspos = self._walker.get_focus()
                    self._walker.expand(focuspos)
            # This is a hack around ListBox misbehaving:
            # it seems impossible to set the focus without calling keypress as
            # otherwise the change becomes visible only after the next render()
            return self._outer_list.keypress(size, None)
        else:
            return self._outer_list.keypress(size, key)


NO_SPACE_MSG = 'too little space for requested decoration'


class TreeDecorationError(Exception):
    pass


class CachingMixin(object):
    """Mixin that allows TreeListWalkers to cache constructed line-widgets"""
    def __init__(self, load, nextpos=None, prevpos=None, **kwargs):
        self._cache = {}
        self.load = load
        self._next_cache = {}
        self._next_position = nextpos
        self._prev_cache = {}
        self._prev_position = prevpos

    def __getitem__(self, pos):
        candidate = None
        if pos in self._cache:
            candidate = self._cache[pos]
        else:
            candidate = self.load(pos)
            self._cache[pos] = candidate
        return candidate

    def next_position(self, pos):
        candidate = self._next_cache.get(pos, None)
        if candidate is None and self._next_position is not None:
            candidate = self._next_position(self, pos)
            self._next_cache[pos] = candidate
        return candidate

    def prev_position(self, pos):
        candidate = self._prev_cache.get(pos, None)
        if candidate is None and self._prev_position is not None:
            candidate = self._prev_position(self, pos)
            self._prev_cache[pos] = candidate
        return candidate


class SelectableIcon(urwid.WidgetWrap):
    """selectable Text widget that handles keypresses with given callable"""
    def __init__(self, txt, handle_keypress=None):
        self._handle_keypress = handle_keypress
        urwid.WidgetWrap.__init__(self, Text(txt))

    def selectable(self):
        return True

    def keypress(self, size, key):
        if self._handle_keypress:
            key = self._handle_keypress(key)
        return key


class CollapseMixin(object):
    """
    Mixin for TreeListWalker that allows to collapse subtrees.
    This works by overwriting `(last|first)_child_position`, forcing them to
    return `None` if the given position is considered collapsed. We use a
    (given) callable `is_collapsed` that accepts positions and returns a boolean
    to determine which node is considered collapsed.
    """
    def __init__(self, is_collapsed=lambda pos: False,
                 **kwargs):
        self._initially_collapsed = is_collapsed
        self._divergent_positions = []

    def is_collapsed(self, pos):
        collapsed = self._initially_collapsed(pos)
        if pos in self._divergent_positions:
            collapsed = not collapsed
        return collapsed

    def last_child_position(self, pos):
        if self.is_collapsed(pos):
            return None
        return self._walker.last_child_position(pos)

    def first_child_position(self, pos):
        if self.is_collapsed(pos):
            return None
        return self._walker.first_child_position(pos)

    def set_position_collapsed(self, pos, is_collapsed):
        if self._initially_collapsed(pos) == is_collapsed:
            if pos in self._divergent_positions:
                self._divergent_positions.remove(pos)
                signals.emit_signal(self, "modified")
        else:
            if pos not in self._divergent_positions:
                self._divergent_positions.append(pos)
                signals.emit_signal(self, "modified")

    def toggle_collapsed(self, pos):
        self.set_position_collapsed(pos, not self.is_collapsed(pos))

    def collapse(self, pos):
        self.set_position_collapsed(pos, True)

    def expand(self, pos):
        self.set_position_collapsed(pos, False)


class CollapseIconMixin(CollapseMixin):
    """
    Mixin for TreeListWalker that allows to allows to collapse subtrees.
    This Mixin adds the ability to construct collapse-icon for a
    position, indicating its collapse status to :class:`CollapseMixin`.
    """
    def __init__(self,
                 is_collapsed=lambda pos: False,
                 icon_collapsed_char='+',
                 icon_expanded_char='-',
                 icon_collapsed_att=None,
                 icon_expanded_att=None,
                 icon_frame_left_char='[',
                 icon_frame_right_char=']',
                 icon_frame_att=None,
                 selectable_icons=False,
                 icon_focussed_att=None,
                 **kwargs):
        CollapseMixin.__init__(self, is_collapsed, **kwargs)
        self._icon_collapsed_char = icon_collapsed_char
        self._icon_expanded_char = icon_expanded_char
        self._icon_collapsed_att = icon_collapsed_att
        self._icon_expanded_att = icon_expanded_att
        self._icon_frame_left_char = icon_frame_left_char
        self._icon_frame_right_char = icon_frame_right_char
        self._icon_frame_att = icon_frame_att
        self._selectable_icons = selectable_icons
        self._icon_focussed_att = icon_focussed_att

    def _construct_collapse_icon(self, pos):
        width = 0
        widget = None
        char = self._icon_expanded_char
        charatt = self._icon_expanded_att
        if self.is_collapsed(pos):
            char = self._icon_collapsed_char
            charatt = self._icon_collapsed_att
        if char is not None:

            columns = []
            if self._icon_frame_left_char is not None:
                lchar = self._icon_frame_left_char
                charlen = len(lchar)
                leftframe = Text((self._icon_frame_att, lchar))
                columns.append((charlen, leftframe))
                width += charlen

            # next we build out icon widget: we feed all markups to a Text,
            # make it selectable (to toggle collapse) if requested
            markup = (charatt, char)
            if self._selectable_icons:
                def keypress(key):
                    if key == 'enter':
                        self.toggle_collapsed(pos)
                        key = None
                    return key
                widget = SelectableIcon(markup, keypress)
                widget = AttrMap(
                    widget, None, focus_map=self._icon_focussed_att)
            else:
                widget = Text(markup)
            charlen = len(char)
            columns.append((charlen, widget))
            width += charlen

            if self._icon_frame_right_char is not None:
                rchar = self._icon_frame_right_char
                charlen = len(rchar)
                rightframe = Text((self._icon_frame_att, rchar))
                columns.append((charlen, rightframe))
                width += charlen

            widget = urwid.Columns(
                columns)  # , box_columns=range(len(columns)))
        return width, widget


class CollapsibleTreeListWalker(CollapseMixin, TreeListWalker):
    def __init__(self, treelistwalker, **kwargs):
        TreeListWalker.__init__(self, treelistwalker, **kwargs)
        CollapseMixin.__init__(self, **kwargs)


class IndentedTreeListWalker(TreeListWalker):
    """
    A TreeListWalker that indents tree nodes to the left according to their
    depth in the tree.
    """
    def __init__(self, treewalker, indent=2, **kwargs):
        self._indent = indent
        TreeListWalker.__init__(self, treewalker, **kwargs)

    def __getitem__(self, pos):
        return self._construct_line(pos)

    def _construct_line(self, pos):
        """
        builds a list element for given position in the tree.
        It consists of the original widget taken from the TreeWalker and some
        decoration columns depending on the existence of parent and sibbling
        positions. The result is a urwid.Culumns widget.
        """
        line = None
        if pos is not None:
            indent = self._walker.depth(pos) * self._indent
            cols = [(indent, urwid.SolidFill(' ')),  # spacer
                    self._walker[pos]]  # original widget ]
            # construct a Columns, defining all spacer as Box widgets
            line = urwid.Columns(cols, box_columns=range(len(cols))[:-1])
        return line

# TODO: broken!
class CollapsibleIndentedTreeListWalker(CollapseIconMixin, CachingMixin, IndentedTreeListWalker):
    def __init__(self, treelistwalker, icon_offset=1, **kwargs):
        self._icon_offset = icon_offset
        IndentedTreeListWalker.__init__(self, treelistwalker, **kwargs)
        CollapseIconMixin.__init__(self, **kwargs)
        CachingMixin.__init__(self, self._construct_line, **kwargs)

    def _construct_line(self, pos):
        """
        builds a list element for given position in the tree.
        It consists of the original widget taken from the TreeWalker and some
        decoration columns depending on the existence of parent and sibbling
        positions. The result is a urwid.Culumns widget.
        """
        void = SolidFill(' ')
        line = None
        if pos is not None:
            cols = []
            depth = self._walker.depth(pos)
            if depth > 0:
                cols.append(
                    (depth * self._indent, urwid.SolidFill(' '))),  # spacer

            # add icon only for non-leafs
            iwidth, icon = self._construct_collapse_icon(pos)
            spacer_width = self._icon_offset + iwidth

            if self._walker.first_child_position(pos) is not None:
                if icon is not None:
                    icon_pile = urwid.Pile([('pack', icon), void])
                    cols.append((iwidth, icon_pile))

                    # spacer until original widget
                    spacer_width = self._icon_offset
            if spacer_width > 0:
                cols.append((spacer_width, SolidFill(' ')))

            cols.append(self._walker[pos])  # original widget ]
            # construct a Columns, defining all spacer as Box widgets
            line = urwid.Columns(cols, box_columns=range(len(cols))[:-1])

        return line

    def set_position_collapsed(self, pos, is_collapsed):
        """needs to be overwritten as CollapseMixin doens't empty the caches"""
        CollapseMixin.set_position_collapsed(self, pos, is_collapsed)
        if pos in self._cache:
            del(self._cache[pos])
        if pos in self._next_cache:
            del(self._next_cache[pos])
        if pos in self._prev_cache:
            del(self._prev_cache[pos])


class ArrowTreeListWalker(CachingMixin, IndentedTreeListWalker):
    """
    TreeListWalker that decorates three, indenting nodes according to their
    depth and drawing arrows to indicate the tree structure.
    """
    def __init__(self, walker, indent=12,
                 childbar_offset=0,
                 arrow_hbar_char=u'\u2500',
                 arrow_hbar_att=None,
                 arrow_vbar_char=u'\u2502',
                 arrow_vbar_att=None,
                 arrow_tip_char=u'\u27a4',
                 arrow_tip_att=None,
                 arrow_att=None,
                 arrow_connector_tchar=u'\u251c',
                 arrow_connector_lchar=u'\u2514',
                 arrow_connector_att=None, **kwargs):
        IndentedTreeListWalker.__init__(self, walker, indent, **kwargs)
        CachingMixin.__init__(self, self._construct_line,
                              nextpos=IndentedTreeListWalker.next_position,
                              prevpos=IndentedTreeListWalker.prev_position,
                              **kwargs)
        self._childbar_offset = childbar_offset
        self._arrow_hbar_char = arrow_hbar_char
        self._arrow_hbar_att = arrow_hbar_att
        self._arrow_vbar_char = arrow_vbar_char
        self._arrow_vbar_att = arrow_vbar_att
        self._arrow_connector_lchar = arrow_connector_lchar
        self._arrow_connector_tchar = arrow_connector_tchar
        self._arrow_connector_att = arrow_connector_att
        self._arrow_tip_char = arrow_tip_char
        self._arrow_tip_att = arrow_tip_att
        self._arrow_att = arrow_att

    def _construct_spacer(self, pos, acc):
        """
        build a spacer that occupies the horizontally indented space between
        pos's parent and the root node. It will return a list of tuples to be
        fed into a Columns widget.
        """
        parent = self._walker.parent_position(pos)
        if parent is not None:
            grandparent = self._walker.parent_position(parent)
            if self._indent > 0 and grandparent is not None:
                parent_sib = self._walker.next_sibbling_position(parent)
                draw_vbar = parent_sib is not None and self._arrow_vbar_char is not None
                space_width = self._indent - 1 * (
                    draw_vbar) - self._childbar_offset
                if space_width > 0:
                    void = AttrMap(urwid.SolidFill(' '), self._arrow_att)
                    acc.insert(0, ((space_width, void)))
                if draw_vbar:
                    barw = urwid.SolidFill(self._arrow_vbar_char)
                    bar = AttrMap(
                        barw, self._arrow_vbar_att or self._arrow_att)
                    acc.insert(0, ((1, bar)))
            return self._construct_spacer(parent, acc)
        else:
            return acc

    def _construct_connector(self, pos):
        """
        build widget to be used as "connector" bit between the vertical bar
        between sibblings and their respective horizontab bars leading to the
        arrow tip
        """
        # connector symbol, either L or |- shaped.
        connectorw = None
        connector = None
        if self._walker.next_sibbling_position(pos) is not None:  # |- shaped
            if self._arrow_connector_tchar is not None:
                connectorw = Text(self._arrow_connector_tchar)
        else:  # L shaped
            if self._arrow_connector_lchar is not None:
                connectorw = Text(self._arrow_connector_lchar)
        if connectorw is not None:
            att = self._arrow_connector_att or self._arrow_att
            connector = AttrMap(connectorw, att)
        return connector

    def _construct_arrow_tip(self, pos):
        """returns arrow tip as (width, widget)"""
        arrow_tip = None
        width = 0
        if self._arrow_tip_char:
            txt = Text(self._arrow_tip_char)
            arrow_tip = AttrMap(txt, self._arrow_tip_att or self._arrow_att)
            width = len(self._arrow_tip_char)
        return width, arrow_tip

    def _construct_first_indent(self, pos):
        """
        build spacer to occupy the first indentation level from pos to the
        left. This is separate as it adds arrowtip and sibbling connector.
        """
        cols = []
        void = AttrMap(urwid.SolidFill(' '), self._arrow_att)
        available_width = self._indent

        if self._walker.depth(pos) > 0:
            logging.debug('available_width=%d' % (available_width))
            connector = self._construct_connector(pos)
            if connector is not None:
                width = connector.pack()[0]
                if width > available_width:
                    raise TreeDecorationError(NO_SPACE_MSG)
                available_width -= width
                if self._walker.next_sibbling_position(pos) is not None:
                    barw = urwid.SolidFill(self._arrow_vbar_char)
                    below = AttrMap(barw, self._arrow_vbar_att or
                                    self._arrow_att)
                else:
                    below = void
                # pile up connector and bar
                spacer = urwid.Pile([('pack', connector), below])
                cols.append((width, spacer))

            logging.debug('available_width=%d' % (available_width))
            #arrow tip
            awidth, at = self._construct_arrow_tip(pos)
            if at is not None:
                if awidth > available_width:
                    logging.debug('awidth=%d available_width=%d' % (awidth,available_width))
                    raise TreeDecorationError(NO_SPACE_MSG)
                available_width -= awidth
                at_spacer = urwid.Pile([('pack', at), void])
                cols.append((awidth, at_spacer))

            # bar between connector and arrow tip
            if available_width > 0:
                barw = urwid.SolidFill(self._arrow_hbar_char)
                bar = AttrMap(barw, self._arrow_hbar_att or self._arrow_att)
                hb_spacer = urwid.Pile([(1, bar), void])
                cols.insert(1, (available_width, hb_spacer))
        return cols

    def _construct_line(self, pos):
        """
        builds a list element for given position in the tree.
        It consists of the original widget taken from the TreeWalker and some
        decoration columns depending on the existence of parent and sibbling
        positions. The result is a urwid.Culumns widget.
        """
        line = None
        if pos is not None:
            original_widget = self._walker[pos]
            cols = self._construct_spacer(pos, [])

            # Construct arrow leading from parent here,
            # if we have a parent and indentation is turned on
            if self._indent > 0:
                indent = self._construct_first_indent(pos)
                if indent is not None:
                    cols = cols + indent

            # add the original widget for this line
            cols.append(original_widget)
            # construct a Columns, defining all spacer as Box widgets
            line = urwid.Columns(cols, box_columns=range(len(cols))[:-1])
        return line


class CollapsibleArrowTreeListWalker(CollapseIconMixin, ArrowTreeListWalker):
    """Arrow- decorated TLW that allows collapsing subtrees"""
    def __init__(self, treelistwalker, icon_offset=0, indent=5, **kwargs):
        self._icon_offset = icon_offset
        ArrowTreeListWalker.__init__(self, treelistwalker, indent, **kwargs)
        CollapseIconMixin.__init__(self, **kwargs)

    def _construct_arrow_tip(self, pos):

        cols = []
        overall_width = self._icon_offset

        if self._icon_offset > 0:
            # how often do we repeat the hbar_char until width icon_offset is reached
            hbar_char_count = len(self._arrow_hbar_char) / self._icon_offset
            barw = Text(self._arrow_hbar_char * hbar_char_count)
            bar = AttrMap(barw, self._arrow_hbar_att or self._arrow_att)
            cols.insert(1, (self._icon_offset, bar))

        # add icon only for non-leafs
        if self._walker.first_child_position(pos) is not None:
            iwidth, icon = self._construct_collapse_icon(pos)
            if icon is not None:
                cols.insert(0, (iwidth, icon))
                overall_width += iwidth

        # get arrow tip
        awidth, tip = ArrowTreeListWalker._construct_arrow_tip(self, pos)
        if tip is not None:
            cols.append((awidth, tip))
            overall_width += awidth

        return overall_width, Columns(cols)

    def set_position_collapsed(self, pos, is_collapsed):
        """needs to be overwritten as CollapseMixin doens't empty the caches"""
        CollapseMixin.set_position_collapsed(self, pos, is_collapsed)
        if pos in self._cache:
            del(self._cache[pos])
        if pos in self._next_cache:
            del(self._next_cache[pos])
        if pos in self._prev_cache:
            del(self._prev_cache[pos])
