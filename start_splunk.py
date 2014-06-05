import os
import subprocess
import sys
from optparse import OptionParser

SPLUNK_DIR = os.path.expanduser("~/splunk_run")
ITEM_PER_ROW = 3


def pick_branch(splunk_directory):
    branches = os.listdir(splunk_directory)

    print "Pick a branch:"
    count = 0
    for branch in branches:
        sys.stdout.write("{i:2d}) {b:8s}\t".format(i=count, b=branch))
        count += 1
        if (count % ITEM_PER_ROW) == 0:
            sys.stdout.write("\n")

    try:
        index = int(raw_input())
        return branches[index]
    except ValueError:
        print "You should enter an integer"
        exit(1)


def pick_build(splunk_directory, branch, latest):
    branch_path = os.path.join(splunk_directory, branch)

    try:
        builds = os.listdir(branch_path)
        builds.sort()
        if not latest:
            print "Pick a build"
            count = 0
            for build in builds:
                sys.stdout.write("{i:2d}) {b:10s}\t".format(i=count, b=build))
                count += 1
                if (count % ITEM_PER_ROW) == 0:
                    sys.stdout.write("\n")

            index = int(raw_input())
            return builds[index]
        else:
            return builds[-1]

    except ValueError:
        print "You should enter an integer"
        exit(1)
    except OSError, err:
        print "Wrong branch name was given"
        print err
        exit(1)

def startsplunk(splunk_home=None):
    """
    Start splunk
    """
    cmd = (os.path.join(splunk_home, "bin", "splunk") +
           " start --answer-yes --accept-license")
    print "Starting splunk..."
    print splunk_home
    p = subprocess.Popen(cmd, env=os.environ, shell=True,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.wait()

def parse_options():
    """
    parse options
    """
    parser = OptionParser()
    parser.add_option("-b", "--branch", dest="branch", help="brach to fetch")
    parser.add_option("-l", "--latest", dest="latest", action="store_true",
                      help="add this option to start the latest build of the branch")
    parser.add_option("-s", "--splunk-dir", dest="splunk_dir",
                      default=SPLUNK_DIR,
                      help="directory for untaring splunk,"
                           "will mkdir if it does not exist")
    (options, args) = parser.parse_args()
    return options

def main():
    options = parse_options()
    branch = (pick_branch(options.splunk_dir) if options.branch is None
              else options.branch)
    build = pick_build(options.splunk_dir, branch, options.latest)
    splunk_home = os.path.join(options.splunk_dir, branch, build, "splunk")

    startsplunk(splunk_home)

if __name__ == '__main__':
    main()
