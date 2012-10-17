import urwid
#import logging


class TreeBoxError(Exception):
    pass


class ListWalkerAdapter(urwid.ListWalker):
    def __init__(self, walker, indent=2,
                 arrow_hbar_char=u'\u2500',
                 arrow_hbar_att=None,
                 arrow_vbar_char=u'\u2502',
                 arrow_vbar_att=None,
                 arrow_tip_char=u'\u27a4',
                 arrow_tip_att=None,
                 void_att=None,
                 arrow_connector_tchar=u'\u251c',
                 arrow_connector_lchar=u'\u2514',
                 arrow_connector_att=None):
        self._walker = walker
        self._indent = indent
        self._arrow_hbar_char = arrow_hbar_char
        self._arrow_hbar_att = arrow_hbar_att
        self._arrow_vbar_char = arrow_vbar_char
        self._arrow_vbar_att = arrow_vbar_att
        self._arrow_connector_lchar = arrow_connector_lchar
        self._arrow_connector_tchar = arrow_connector_tchar
        self._arrow_connector_att = arrow_connector_att
        self._arrow_tip_char = arrow_tip_char
        self._arrow_tip_att = arrow_tip_att
        self._void_att = void_att
        self._cache = {}

    def get_focus(self):
        widget, position = self._walker.get_focus()
        return self[position], position

    def set_focus(self, pos):
        return self._walker.set_focus(pos)

    def next_position(self, pos):
        return self._walker.next_position(pos)

    def prev_position(self, pos):
        return self._walker.prev_position(pos)

    def __getitem__(self, pos):
        candidate = None
        if pos in self._cache:
            candidate = self._cache[pos]
        else:
            candidate = self._construct_line(pos)
            self._cache[pos] = candidate
        return candidate

    def _construct_spacer(self, pos, acc):
        """
        build a spacer that occupies the horizontally indented
        space between pos and the root node.
        It will return a list of tuples to be fed into a Columns
        widget.
        """
        parent = self._walker.parent_position(pos)
        if parent is not None:
            grandparent = self._walker.parent_position(parent)
            if self._indent > 0 and grandparent is not None:
                parent_sib = self._walker.next_sibbling_position(parent)
                space_width = self._indent - 1 * (parent_sib is not None)
                if space_width > 0:
                    void = urwid.AttrMap(urwid.SolidFill(' '), self._void_att)
                    acc.insert(0, ((space_width, void)))
                if parent_sib is not None:
                    barw = urwid.SolidFill(self._arrow_vbar_char)
                    bar = urwid.AttrMap(barw, self._arrow_vbar_att)
                    acc.insert(0, ((1, bar)))
            return self._construct_spacer(parent, acc)
        else:
            return acc

    def _construct_line(self, pos):
        """
        builds a list element for given position in the tree.
        It consists of the original widget taken from the TreeWalker
        and some decoration columns depending on the existence
        of parent and sibbling positions.
        The result is a urwid.Culumns widget.
        """
        line = None
        if pos is not None:
            original_widget = self._walker[pos]
            cols = self._construct_spacer(pos, [])
            parent = self._walker.parent_position(pos)

            # Construct arrow leading from parent here,
            # if we have a parent and indentation is turned on
            if self._indent > 0 and parent is not None:
                void = urwid.AttrMap(urwid.SolidFill(' '), self._void_att)
                # connector symbol, either L or |- shaped.
                # wrap the char into a SolidFill
                if self._walker.next_sibbling_position(pos) is not None:  # |- shaped
                    connectorw = urwid.SolidFill(self._arrow_connector_tchar)
                else:  # L shaped
                    connectorw = urwid.SolidFill(self._arrow_connector_lchar)
                # wrap the widget into an AttrMap to apply colouring attribute
                connector = urwid.AttrMap(connectorw, self._arrow_vbar_att)
                # construct vertical bar part
                barw = urwid.SolidFill(self._arrow_vbar_char)
                bar = urwid.AttrMap(barw, self._arrow_vbar_att)
                # pile up connector and bar
                spacer = urwid.Pile([(1, connector), void])
                cols.append((1, spacer))

                # bar between connector and arrow tip
                if self._indent > 2:
                    barw = urwid.SolidFill(self._arrow_hbar_char)
                    bar = urwid.AttrMap(barw, self._arrow_hbar_att)
                    hb_spacer = urwid.Pile([(1, bar), void])
                    cols.append((self._indent - 2, hb_spacer))
                #arrow tip
                if self._indent > 1:
                    arrow_tip = urwid.SolidFill(self._arrow_tip_char)
                    at = urwid.AttrMap(arrow_tip, self._arrow_tip_att)
                    hb_spacer = urwid.Pile([(1, at), void])
                    cols.append((1, hb_spacer))

            # add the original widget for this line
            cols.append(original_widget)
            # construct a Columns, defining all spacer as Box widgets
            line = urwid.Columns(cols, box_columns=range(len(cols))[:-1])
        return line


class TreeBox(urwid.WidgetWrap):
    """A widget representing something in a nested tree display."""
    _selectable = True

    def __init__(self, walker, **kwargs):
        self._walker = walker
        self._adapter = ListWalkerAdapter(walker, **kwargs)
        self._outer_list = urwid.ListBox(self._adapter)
        self.__super.__init__(self._outer_list)

    def get_focus(self):
        return self._outer_list.get_focus()

    def focus_parent(self):
        parent = self._walker.parent_position(self._walker.focus)
        if parent is not None:
            self._outer_list.set_focus(parent)

    def focus_first_child(self):
        child = self._walker.first_child_position(self._walker.focus)
        if child is not None:
            self._outer_list.set_focus(child)

    def focus_next_sibbling(self):
        sib = self._walker.next_sibbling_position(self._walker.focus)
        if sib is not None:
            self._outer_list.set_focus(sib)

    def focus_prev_sibbling(self):
        sib = self._walker.prev_sibbling_position(self._walker.focus)
        if sib is not None:
            self._outer_list.set_focus(sib)

    def keypress(self, size, key):
        """
        TreeBox interprets `left/right` as well as page `up/down` to move the
        focus to parent/first child and next/previous sibbling respectively.
        All other keys are passed to the underlying ListBox.
        """
        if key in ['left', 'right', 'page up', 'page down']:
            if key == 'left':
                self.focus_parent()
            elif key == 'right':
                self.focus_first_child()
            elif key == 'page up':
                self.focus_prev_sibbling()
            elif key == 'page down':
                self.focus_next_sibbling()
            # This is a hack around ListBox misbehaving:
            # it seems impossible to set the focus without calling keypress as
            # otherwise the change becomes visible only after the next render()
            return self._outer_list.keypress(size, None)
        else:
            return self._outer_list.keypress(size, key)
