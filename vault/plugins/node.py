
import logging

logger = logging.getLogger(__name__)

class Node:

    def __init__(self, root):
        self.root = root

    def do_show(self, *args):
        """ Print some representation of the given node. """
        node = self.root.query(*args)
        if not node:
            logger.error("path not found: %s", "/".join(args))
        else:
            print(node.show())
