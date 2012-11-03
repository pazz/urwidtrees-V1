Urwid Tree Container API
========================

This is a POC implementation of a new Widget Container API for the [urwid][urwid] toolkit.
Its design goals are

* clear separation classes that define, decorate and display trees of widgets
* representation of trees by local operations on node positions
* easy to use default implementation for simple trees
* Collapses are considered decoration

We propose a `urwid.ListBox`-based widget that display trees where siblings grow vertically and
children horizontally.  This `TreeBox` widget handles key presses to move in the tree and
collapse/expand subtrees if possible.

The choice to define trees by overwriting local position movements allows to
easily define potentially infinite tree structures. See `example4` for how to
walk local file systems.

The overall structure of the API contains three parts:

walkers.TreeWalker
------------------
Objects of this type define a tree structure by implementing the local movement methods

    parent_position
    first_child_position
    last_child_position
    next_sibling_position
    prev_sibling_position

Each of which takes and returns a `position` object of arbitrary type (fixed for the walker)
as done in urwids ListWalker API. Apart from this, walkers need to define a dedicated position
`walker.root` that is used as fallback initially focussed element,
and define the `__getitem__` method to return some Widget for a given position.

widgets.TreeBox
---------------
Is essentially a `urwid.ListBox` that displays a given `TreeWalker`. Per default no decoration is used
and the widgets of the tree are simply displayed line by line in depth first order.
`TreeBox`'s constructor accepts a `focus` parameter to specify the initially focussed position.

widgets.TreeListWalker
----------------------
Objects of this type serve as adapter between TreeWalker and ListWalker APIs:
They implement the ListWalker API using the data from a given `TreeWalker` in depth-first order.
`TreeListWalker` may introduce decoration for tree nodes. This package offers a few
readily usable `TreeListWalker` subclasses that implement decoration by indentation, arrow shapes
and subtree collapsing.
As such, one can directly pass on a `TreeListWalker` to an `urwid.ListBox` if one doesn't want
to use tree-based focus movement or key bindings for collapsing subtrees.

[urwid]: http://excess.org/urwid/
