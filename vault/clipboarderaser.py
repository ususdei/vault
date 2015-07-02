#!/usr/bin/env python

import sys
import time
import subprocess

delay = 45
try:
    delay = abs(int(sys.argv[1]))
except:
    pass
time.sleep(delay)
clip = subprocess.Popen("xclip -selection clipboard".split(), stdin=subprocess.PIPE)
clip.communicate(input=b'__empty__')

