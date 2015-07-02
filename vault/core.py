
import logging
import os

logger = logging.getLogger(__name__)

class Item:
    """ Abstract Item
        -------------
        Vault has a hierarchical tree-like notion of the values it can retrieve.
        Every node in this tree is an `Item`.
        All items store:

        type
            An identifier for this node type.

        path
            The entire path in vaults notion to reach this node

        name
            The name of this node.
            Should also be the last part of its path.

        children
            An iterable over all subnodes this node has.
    """

    type = "item"

    def __init__(self, *args, **kwargs):
        self.path = None
        self.name = None
        raise NotImplementedError()

    @property
    def children(self):
        return []

    def get(self):
        """ Return the most sensible Value in this subtree or None. """
        return None

    def query(self, q):
        """ Return the most sensible Item that matches `q` in this subtree or None. """
        for c in self.children:
            if c.name == q:
                return c
        if len(self.children) == 1:
            return self.children[0].query(q)
        for c in self.children:
            if c.name == "default":
                return c.query(q)
        for c in self.children:
            if c.name == os.environ['USER']:
                return c.query(q)
        return None

    def find(self, name):
        """ Return a list of all Values with name `name` in this subtree. """
        r = []
        for c in self.children:
            r.extend(c.find(name))
        return r

    def show(self):
        """ Return a string representation of this subtree. """
        #TODO: treeview
        pass

    def edit(self):
        """ Provide a possibility to edit this subtree. """
        raise NotImplementedError()



class Value(Item):
    """ Value
        -----
        A Value is also an Item but it is always a leaf.
        This is where the actual values are stored.
    """

    type = "value"

    def __init__(self, path, name, value):
        self.path = path
        self.name = name
        self.value = value

    @property
    def children(self):
        return []

    def get(self):
        return self

    def query(self, q):
        None

    def find(self, name):
        if self.name == name:
            return [self]
        return []

    def show(self):
        return self.value

    def edit(self):
        raise NotImplementedError()






class Root:
    """ Root
        ----
        Root is used to represent the entire tree `vault` knows of.
        It provides a possibility to mount different password-stores in the tree.
    """

    def __init__(self):
        self.mounts = {}

    def mount(self, mountpoint, item):
        self.mounts[mountpoint] = item

    def query(self, *args):
        """ Return the most sensible Item that matches the given path or None. """
        qs = "/".join(args).split("/")
        if qs[0] in self.mounts:
            c = self.mounts.get(qs[0])
            qs = qs[1:]
        else:
            c = self.mounts.get("", None)
        while qs:
            c = c.query(qs[0])
            if c is None:
                return None
            qs = qs[1:]
        return c

    def find(self, name):
        """ Return a list of all Values with name `name`. """
        r = []
        for c in self.mounts.values():
            r.extend(c.find(name))
        return r


