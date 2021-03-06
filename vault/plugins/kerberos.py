

import logging
import subprocess

from .. import util

logger = logging.getLogger(__name__)

class Kerberos:

    def __init__(self, root):
        self.root = root

    def do_init(self):
        """ Feed kinit with Kerberos credentials. """
        for d in util.get_dict_by_name(self.root, 'principal'):
            principal = d.get('principal', None)
            pw        = d.get('password', None)  
            if principal and pw:
                logger.debug("Getting ticket for %s", principal)
                kinit = subprocess.Popen(['kinit', principal], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL)
                kinit.stdin.write(pw.encode("utf-8"))
                kinit.stdin.close()
                kinit.wait()
        return

