
from . import wifi
from . import ssh
from . import kerberos
from . import node


PLUGINS = [node.Node, wifi.Wifi, ssh.Ssh, kerberos.Kerberos]

