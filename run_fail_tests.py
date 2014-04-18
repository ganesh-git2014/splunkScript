from selenium.webdriver.firefox.webdriver import WebDriver as Firefox
import sys
import subprocess
import os
from optparse import OptionParser

P4_DIR = os.path.join(os.path.expanduser("~"), "Documents", "p4depot", "splunk")

def get_fail_tests(url):
    """
    """
    browser = Firefox()
    browser.get(url)
    # get new failures
    tests = [e.text.strip() for e in
             browser.find_elements_by_css_selector(
             "#new-failed-tests .test-name")]

    # get existing tests
    tests = tests + [e.text.strip() for e in
                     browser.find_elements_by_css_selector(
                     "#existing-failed-tests .test-name")]
    browser.quit()
    return tests

def get_keywords(tests):
    """
    """
    return [t.replace("[", " ").replace("]", " ").replace("-", " ")
            for t in tests]

def parse_options():
    """
    parse options
    """
    parser = OptionParser()
    parser.add_option("-b", "--branch", dest="branch", help="brach to test",
                      default="bubbles")
    parser.add_option("-s", "--splunk-home", dest="splunk_home",
                      help="The splunk instance to test against")
    parser.add_option("-u", "--url", dest="url",
                      help="bamboo url to get the test result")
    parser.add_option("-f", "--keyword_file", dest="keyword_file",
                      help="Instead of getting tests from bamboo,"
                            "get tests to run in a file")
    parser.add_option("-p", "--p4-dir", dest="p4_dir",
                      help="your p4 directory, it should ends with 'splunk'",
                      default=P4_DIR)
    (options, args) = parser.parse_args()
    return options

def check_test_dir(directory):
    """
    """
    if not os.path.exists(directory):
        print "Can not find {t}".format(t=directory)
        print "Did you provide correct p4_dir and branch?"
        exit(1)

def get_result_line(lines, keyword):
    """
    """
    for line in lines:
        if keyword in line:
            return line

def main():
    options = parse_options()
    bamboo_url = options.url
    splunk_home = options.splunk_home
    test_dir = os.path.join(options.p4_dir, "branches", options.branch,
                            "new_test")
    check_test_dir(test_dir)

    # get tests to run
    if options.keyword_file is not None:
        f = open(options.keyword_file, "r")
        keywords = [line.strip() for line in f.readlines()]
        f.close()
    elif bamboo_url is not None:
        keywords = get_keywords(get_fail_tests(bamboo_url))
    else:
        print "You have to specify either bamboo_url or keyword file"
        exit(1)

    print "Found {n} failed tests".format(n=len(keywords))

    # run tests
    result_file = open("run_fail_tests.log", "w")  # for logging the result
    for keyword in keywords:
        cmd = ("cd {t}; source setTestEnv {s}; cd tests/web/webdriver; pwd; "
               "{s}/bin/splunk cmd python {t}/bin/pytest/pytest.py -k '{k}'"
               .format(t=test_dir, s=splunk_home, k=keyword))
        p = subprocess.Popen(cmd, env=os.environ, shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()

        result_line = p.stdout.readlines()[8]
        if result_line.endswith("PASSED\n"):
            print "{k}: PASSED".format(k=keyword)

        elif result_line.endswith("FAILED\n"):
            result_file.write(keyword + "\n")
            print "{k}: FAILED".format(k=keyword)

        else:
            result_file.write(keyword + "\n")
            print "{k}: ERROR".format(k=keyword)
    result_file.close()

if __name__ == '__main__':
    main()
