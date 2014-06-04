import os
import subprocess
import sys
from threading import Thread

def stop_splunk(splunk_home):
    """
    """
    print "Stopping {s}".format(s=splunk_home)

    cmd = "{spl}/bin/splunk stop".format(spl=splunk_home)

    p = subprocess.Popen(cmd, env=os.environ, shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()


p = subprocess.Popen("ps aux | grep splunk", env=os.environ, shell=True,
                     stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
p.wait()
target = "python -O"
splunks = [ p[p.find(target) + len(target): p.find("/lib")]
            for p in p.stdout.readlines() if p.find(target) != -1]

if "-all" in sys.argv:
    print "Stopping all splunk"
    for spl in splunks:
        t = Thread(target=stop_splunk, args=(spl,))
        t.start()
else:
    if 1 == len(splunks):
        index = 0
    elif 0 == len(splunks):
        print "No splunk running, exiting..."
        exit(0)
    else:
        c = 0
        for s in splunks:
            print "{c}) {s}".format(c=c, s=s)
            c += 1
        index = int(raw_input())

    print "Stopping {spl}".format(spl=splunks[index])
    stop_splunk(splunks[index])