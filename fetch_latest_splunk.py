import urllib
from optparse import OptionParser
import os
import subprocess
from datetime import datetime
import sys

DEFAULT_PKG_DIR = os.path.join(os.path.expanduser("~"), "branches_tar")
DEFAULT_SPLUNK_DIR = os.path.join(os.path.expanduser("~"), "splunk_run")

def print_time_spent(time, pkg):
    """
    print how much time spent and the avg internet speed
    """
    print "Finished downloading, it took {t} seconds".format(t=time)
    if time > 0:
        speed = (os.path.getsize(pkg) / 1024) / time
        print "Average speed: {s} kilobytes per second".format(s=speed)

def dluntar(url, tar_dir, run_dir, package_name, branch=None):
    """
    Dowload and then untar splunk package, calculate time spent also
    """
    TAR_DIR = tar_dir #"/Users/clin/branches_tar"
    RUN_DIR = run_dir #"/Users/clin/splunk_run"
    # download the tgz file
    # find the brach name and build number
    branch = (url.split("/")[4].replace("_builds", "") if branch is None
              else branch)
    build = (url.split("/")[-1].replace("splunk-", "")
             .replace("-" + package_name, ""))
    file_name = url.split("/")[-1]

    path = os.path.join(TAR_DIR, branch)
    if not os.path.exists(path):
        os.mkdir(path)

    tar_file = os.path.join(TAR_DIR, branch, file_name)
    if not os.path.exists(tar_file):
        try:
            print "Dowloading: {u}".format(u=url)
            print "to: {f}".format(f=tar_file)
            start = datetime.now()
            urllib.urlretrieve(url, tar_file)
            end = datetime.now()
            diff = end - start
            print_time_spent(time=diff.seconds, pkg=tar_file)
        except IOError, err:
            print "Can not open url. Did you connect to Splunk VPN?"
            print "ERROR: " + err
            exit(1)

    # untar the file
    # get path
    branch_path = os.path.join(RUN_DIR, branch)
    if not os.path.exists(branch_path):
        os.mkdir(branch_path)
    untar_path = os.path.join(RUN_DIR, branch, build)
    if not os.path.exists(untar_path):
        os.mkdir(untar_path)

    # if splunk is already there, just exit
    if os.path.exists(os.path.join(untar_path, "splunk")):
        print "Splunk is already in {p}, exiting".format(
                                          p=os.path.join(untar_path, "splunk"))
        exit(0)
    else:
        command = "tar xf {tar} -C {path}".format(tar=tar_file, path=untar_path)
        print "Running '{c}'".format(c=command)
        p = subprocess.Popen(command, env=os.environ, shell=True,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        p.wait()
        print os.path.join(untar_path, "splunk", "bin")

def get_package_names():
    """
    get the package name by system's platform
    """
    platform = sys.platform

    if "linux" in platform:
        return ["Linux-x86_64.tgz"]
    elif "darwin" in platform:
        return ["darwin-64.tgz", "Darwin-universal.tgz"]
    else:
        print "Did not implement for this platform: {p}".format(p=platform)
        exit(1)

def get_host(host):
    """
    get the fetcher hostname
    """
    if not host in ["TW", "SF"]:
        print "Wrong -f argument, please use TW or SF"
    hosts = {"TW": "http://172.18.90.221",
             "SF": 'http://releases.splunk.com'}

    if 200 == urllib.urlopen(hosts[host]).getcode():
        return hosts[host]
    else:
        print "The host {h} is not available".format(h=host)
        print "Existing..."
        exit(1)

def parse_options():
    """
    parse options
    """
    parser = OptionParser()
    parser.add_option("-b", "--branch", dest="branch", help="brach to fetch")
    parser.add_option("-c", "--p4change", dest="cl",
                      help="change list number to fetch")
    parser.add_option("-p", "--pkg-dir", dest="pkg_dir",
                      default=DEFAULT_PKG_DIR,
                      help="directory for saving the pkg, "
                           "will mkdir if it does not exist")
    parser.add_option("-s", "--splunk-dir", dest="splunk_dir",
                      default=DEFAULT_SPLUNK_DIR,
                      help="directory for untaring splunk,"
                           "will mkdir if it does not exist")
    parser.add_option("-u", "--url", dest="url",
                      help="url to the splunk package")
    parser.add_option("-f", "--from", dest="host",
                      help="whre you want to fetch from: TW or SF",
                      default='TW')
    parser.add_option("-l", "--splunklight", help="set this to get splunklight",
                      action="store_true", dest="light")
    (options, args) = parser.parse_args()
    return options

def main():
    options = parse_options()
    branch = options.branch
    cl = options.cl
    pkg_dir = options.pkg_dir
    splunk_dir = options.splunk_dir
    url = options.url
    host = options.host
    light = options.light

    # check if pkg_dir and splunk_dir exist. if not, create them
    if not os.path.exists(pkg_dir):
        os.makedirs(pkg_dir)

    if not os.path.exists(splunk_dir):
        os.makedirs(splunk_dir)

    if url is not None:
        dluntar(url=url, tar_dir=pkg_dir, run_dir=splunk_dir)
    else:
        if branch is None:
            print "Branch must be given, please use '-b' option to specify a branch"
            exit(1)

        # getting the pkg url
        host = get_host(host)
        url_template = (host + "/cgi-bin/splunk_build_fetcher.py?"
                        "PLAT_PKG={p}&DELIVER_AS=url&BRANCH={b}")
        if cl is not None:
            print "Getting splunk on branch '{b}' @ {cl}".format(b=branch, cl=cl)
            url_template = url_template + "&P4CHANGE={c}".format(c=cl)
        else:
            print "Getting the latest splunk pkg on branch '{b}'".format(b=branch)

        if light is not None:
            print "Getting splunk light"
            url_template = url_template + "&PRODUCT=splunklight"
        else:
            print "Getting splunk"

        # get url of latest package
        for p in get_package_names():
            f = urllib.urlopen(url_template.format(b=branch, p=p))
            pkg_url = f.readline().strip()

            if "Error" in pkg_url:
                continue
            else:
                print pkg_url
                # run dluntar
                dluntar(url=pkg_url, tar_dir=pkg_dir, run_dir=splunk_dir,
                        package_name=p, branch=branch)
                break

        if "Error" in pkg_url:
            print pkg_url

if __name__ == '__main__':
    main()

