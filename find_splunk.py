#!/usr/bin/python
import os
import subprocess
import sys

p = subprocess.Popen("ps aux | grep splunk", env=os.environ, shell=True, stdin=subprocess.PIPE,
	             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
p.wait()
processes = p.stdout.readlines()
target = "python -O "
if len(processes) > 1:
    for p in processes:
        pos = p.find(target)
        if -1 != pos:
	    print p[pos + len(target): p.find("/lib")]
else:
    sys.stdout.write(processes[0][pos + len(target): p.find("/lib")])
