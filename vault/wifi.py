
import logging
import os
import os.path
import subprocess

from . import util

logger = logging.getLogger(__name__)

def wifi(root, name=None):
    ifcs = [ i for i in os.listdir('/sys/class/net/') if i.startswith('w')]
    if not ifcs:
        logger.error("No wifi interface found")
        return
    interface = ifcs[0]
    entry = None
    if name:
        for e in util.get_dict_by_name(root, 'SSID'):
            if e.get('name', None) == name:
                entry = e
                break
        else:
            logger.error("No configuration for wifi %s found.", name)
            return
    else:
        confs = { e.get('SSID') : e for e in util.get_dict_by_name(root, 'SSID') }
        cells = []
        quality = 0
        for line in subprocess.check_output(["sudo", "iwlist", interface, "scan"]).decode('UTF-8').splitlines():
            if line.strip().startswith('Quality'):
                cur,_,max = line.split()[0].split('=')[1].partition('/')
                quality = float(cur) / float(max)
            elif line.strip().startswith('ESSID'):
                _,_,ssid = line.partition(':')
                ssid = ssid.strip().strip('"')
                if ssid in confs:
                    logger.debug("Found Cell %s [%f]", ssid, quality)
                    cells.append((quality, confs.get(ssid)))
        if not cells:
            logger.error("No wifi with matching configuration found")
            return
        _,entry = sorted(cells)[-1]
        logger.info("Connecting to %s", entry.get('SSID'))
    interface = entry.get('interface', interface)
    fn        = entry.get('name', None)
    ssid      = entry.get('SSID', fn)
    pw        = entry.get('password', None)
    if interface and fn and ssid and pw:
        pw = pw.splitlines()
        if len(pw) < 2:
            supplicant_conf = subprocess.check_output(["wpa_passphrase", ssid, pw[0]]).decode('UTF-8')
        else:
            supplicant_conf = 'network={\n  %s\n}\n' % ('\n  '.join(pw[1:-1]))
        with util.tempdir() as tmpdir:
            tmpfile = os.path.join(tmpdir, fn)
            with open(tmpfile, "w") as f:
                f.write(supplicant_conf)
            subprocess.call(["sudo", "killall", "wpa_supplicant"])
            subprocess.check_call(["sudo", "ip", "link", "set", "dev", interface, "up"])
            subprocess.check_call(["sudo", "wpa_supplicant", "-B", "-D", "nl80211,wext", "-i", interface, "-c", tmpfile])
            subprocess.call(["sudo", "dhcpcd", interface])
    return
