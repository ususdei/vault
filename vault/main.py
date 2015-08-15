
import logging
logging.basicConfig(level=logging.DEBUG)
import sys
import os.path
import collections
import subprocess
from . import core
from .backend import gpass
from . import plugins

logger = logging.getLogger(__name__)

def main():
    root = core.Root()
    root.mount("", gpass.PassDir(""))
    modules = [ plg(root) for plg in plugins.PLUGINS ]
    actions = collections.OrderedDict()
    for m in modules:
        for k in dir(m):
            if k.startswith("do_"):
                actions[k[3:]] = actions.get(k[3:], []) + [getattr(m, k)]
    if len(sys.argv) < 2:
        print("Usage:")
        print("  %s COMMAND [ARGS ...]" % sys.argv[0])
        print("  %s PATH ..." % sys.argv[0])
        print("")
        print("Commands:")
        print("")
        print("PATH")
        print("   Copy value at PATH to clipboard and erase after some time.")
        for k,v in actions.items():
            print(k)
            for fn in v:
                if hasattr(fn, "__doc__") and fn.__doc__:
                    print("   %s" % fn.__doc__.strip())
    elif sys.argv[1] in actions:
        for fn in actions.get(sys.argv[1]):
            fn(sys.argv[2:])
    else:
        node = root.query(*sys.argv[1:])
        if node is None:
            logger.error("path not found: %s", "/".join(sys.argv[1:]))
            return
        value = node.get()
        if value is None:
            logger.error("value not found: %s", "/".join(sys.argv[1:]))
            return
        clip = subprocess.Popen("xclip -selection clipboard".split(), stdin=subprocess.PIPE)
        clip.communicate(input=value.value.encode("utf-8"))
        eraser = os.path.abspath(os.path.join(os.path.split(__file__)[0], "clipboarderaser.py"))
        subprocess.Popen(["/usr/bin/env", "python", eraser])

