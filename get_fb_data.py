from selenium.webdriver.firefox.webdriver import WebDriver as FireFox
from datetime import datetime
from optparse import OptionParser
import platform
import json
import csv
import os


def get_post_attribute(post):
    '''
    Get share, like, and comment counts
    Get the content of the post

    @param post: WebElement for the facebook post
    @type post: WebElement

    @rtype: dictionary
    @returns: dictionary of the attributes by given post
    '''

    def get_counts(label):
        '''
        label is like: "34428 likes 198 comments 628 shares"
        '''
        tokens = label.split(" ")
        return { "like": tokens[0], "comment": tokens[2], "share": tokens[4] }

    label = (post.find_element_by_css_selector("a[aria-label*='likes']")
        .get_attribute('aria-label'))
    ret = get_counts(label)
    ret['content'] = post.find_element_by_class_name("userContent").text
    return ret

def get_fb_user_posts(browser, row, file_name):
    '''
    Get user's posts and write them to a json file

    @param browser: Browser to get the posts
    @type browser: WebDriver

    @param row: a dictionary of a row of the input file
    @type uri: dictionary
    '''
    browser.get("https://www.facebook.com" + row['uri'])
    # scroll to bottom for 3 times to get more posts
    for i in range(3):
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

    # Get the name
    name = browser.find_element_by_css_selector(
        "h2._58gi").text
    category = browser.find_element_by_css_selector(
        "._58gj.fsxxl.fwn.fcw").text
    posts = browser.find_elements_by_css_selector(
        "._4-u2.mbm._5jmm._5pat._5v3q")

    with open(file_name, "a") as output:
        for post in posts:
            attributes = get_post_attribute(post)
            attributes['fb_name'] = name
            attributes['fb_category'] = category
            attributes['fb_time'] = post.get_attribute("data-time")
            attributes['get_time'] = datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S")
            attributes.update(row)
            json.dump(attributes, output)

def parse_options():
    """
    parse options
    """
    parser = OptionParser()
    parser.add_option(
        "-o", "--output", dest="output", help="file to write output",
        default="fb.json")
    parser.add_option(
        "-i", "--input", dest="input", help="csv file get fb users",
        default="fb_input.csv")
    (options, args) = parser.parse_args()
    return options

def main():
    # start browser
    browser = FireFox()
    try:
        options = parse_options()
        with open(options.input, "r") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                get_fb_user_posts(browser, row, options.output)
    except Exception, e:
        print e
    finally:
        browser.close()

if __name__ == '__main__':
    # start virtual display if running on linux
    if platform.system() == "Linux":
        from xvfbwrapper import Xvfb
        vdisplay = Xvfb()
        vdisplay.start()
    main()

    if platform.system() == "Linux":
        vdisplay.stop()
