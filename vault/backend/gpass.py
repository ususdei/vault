
import os
import os.path
import logging
import subprocess
import re
from .. import core

logger = logging.getLogger(__name__)

# *******************************************
# * Adapter for the "pass" password store
# * it uses gpg encrypted files
# * in a directory structure
# * to store passwords
# *******************************************

ROOT = os.path.expanduser("~/.password-store")
ROOT = os.environ.get("PASSWORD_STORE_DIR", ROOT)

def abspath(path):
    return os.path.join(ROOT, path)

PassValue = core.Value

class PassFile(core.Item):

    type = "passfile"

    def __init__(self, path):
        self.path = path
        self.name = os.path.split(path)[1]
        self._children = None

    def get(self):
        for c in self.children:
            if c.name == "password":
                return c
        return None

    @property
    def children(self):
        if self._children is not None:
            return self._children
        self._children = []
        content = self._decrypt()
        if content is None:
            return []
        if not content:
            logger.warning("Empty file: %s.gpg", self.path)
            return []
        for name,value in self._parse(content).items():
            self._children.append(core.Value(self.path + "/" + name, name, value))
        return self._children

    def show(self):
        return self._decrypt()

    def _decrypt(self):
        try:
            filepath = abspath(self.path + ".gpg")
            cmd = "gpg2 -d --quiet --yes --compress-algo=none --no-encrypt-to --batch --use-agent"
            return subprocess.check_output(cmd.split() + [filepath]).decode('utf-8')
        except subprocess.CalledProcessError as e:
            logger.error("Failed to decrypt file: %s\ngpg2 exited with %d\n%s", filepath, e.returncode, e.output)
        return None

    def _parse(self, content):
        r = {}
        lines = content.splitlines()
        # NOTE: password first
        if lines[0].startswith("-----") and lines[0].endswith("-----"):
            # NOTE: multiline password
            pw = lines[0]
            lines = lines[1:]
            while lines:
                pw = pw + "\n" + lines[0]
                if lines[0].startswith("-----") and lines[0].endswith("-----"):
                    lines = lines[1:]
                    break
                lines = lines[1:]
        else:
            pw = lines[0].strip()
            lines = lines[1:]
        r['password'] = pw
        r['pw']       = pw
        for l in lines:
            fields = re.split(r'[=:]', l, 1)    # NOTE: allow ':' and '=' as separators
            if len(fields)==2 and fields[0].strip():
                r[fields[0].strip()] = fields[1].strip()
            else:
                logger.warning("Meaningless line in %s.gpg\n  %s", self.path, l)
        return r


class PassDir(core.Item):

    type = "passdir"

    def __init__(self, path):
        self.path = path
        self.name = os.path.split(path)[1]
        self._children = None

    @property
    def children(self):
        if self._children is not None:
            return self._children
        self._children = []
        for f in os.listdir(abspath(self.path)):
            path = os.path.join(self.path, f)
            dir  = abspath(path)
            if f.startswith('.') or f.startswith('_'):
                continue
            elif os.path.isdir(dir):
                self._children.append(PassDir(path))
            elif os.path.isfile(dir) and dir.endswith('.gpg'):
                self._children.append(PassFile(path[:-4]))
            else:
                logger.error("Wtf! path: %s", path)
        return self._children

    def show(self):
        #TODO: treeview
        pass





