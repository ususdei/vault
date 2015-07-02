
import logging
import os
import os.path
import tempfile
import subprocess

from .. import util

logger = logging.getLogger(__name__)

def OnInit(root):
    os.umask(0o077)  # NOTE: allow 0600
    with tempfile.TemporaryDirectory() as tmpdir:
        for d in util.get_dict_by_name(root, 'ssh-add'):
            if d.get('ssh-add', 'false').lower() == 'true':
                cert = d.get('password', None)
                name = d.get('name', None)
                if cert and name:
                    logger.debug("Adding certificate %s", name)
                    tmpfile = os.path.join(tmpdir, name)
                    with open(tmpfile, "w") as f:
                        f.write(cert)
                        f.write("\n")
                    subprocess.check_call(["ssh-add", tmpfile])
    return

