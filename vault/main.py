
import logging
logging.basicConfig(level=logging.DEBUG)
import sys
import os.path
import subprocess
from . import core
from .backend import gpass
from . import init
from . import wifi

logger = logging.getLogger(__name__)

def main():
    root = core.Root()
    root.mount("", gpass.PassDir(""))
    if False:
        pass
    elif sys.argv[1] == "init":
        for i in init.INITS:
            if hasattr(i, "OnInit"):
                i.OnInit(root)
    elif sys.argv[1] == "show":
        node = root.query(*sys.argv[2:])
        if not node:
            logger.error("path not found: %s", "/".join(sys.argv[2:]))
        else:
            print(node.show())
    elif sys.argv[1] == "wifi":
        if len(sys.argv) == 3:
            wifi.wifi(root, sys.argv[2])
        else:
            wifi.wifi(root)
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

