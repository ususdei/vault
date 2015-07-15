
import logging
import os
import os.path
import tempfile
import contextlib
import subprocess

logger = logging.getLogger(__name__)

# ***************************************************
# * some utility functions
# * that can be used by plugins
# ***************************************************

def get_dict_by_name(root, name):
    """ Return a list of Nodes that have a child Value with name `name`. """
    r = []
    for v in root.find(name):
        parent,_,n = v.path.rpartition('/')
        if not n == name:
            logger.warning("Name does not match. %s was found using name %s.", v.path, name)
        node = root.query(parent)
        if not node: continue
        d = dict(name=node.name, path=node.path)
        for c in node.children:
            if hasattr(c, 'value'):
                d[c.name] = c.value
        r.append(d)
    return r


@contextlib.contextmanager
def tempdir():
    os.umask(0o077)
    if os.path.isdir('/dev/shm'):
        dir = '/dev/shm'
    else:
        dir = None
    try:
        tmp = tempfile.TemporaryDirectory(dir=dir)
        logger.debug("Created secure temporary directory %s", tmp.name)
        yield tmp.name
    finally:
        for f in os.listdir(tmp.name):
            subprocess.check_call([ "shred", "-fuzn", "5", os.path.join(tmp.name, f) ])
        tmp.cleanup()

