#!/usr/bin/env python
##
# next_meeting.py
###
"""next_meeting.py

Creates the next meeting page from the template on the wiki.
Calculates the next ordinal number for the meeting ie (the 31811th Meeting etc)
Redirects 'Next meeting' and 'Last meeting' pages to point to correct minutes.

"""

__version__ = "0.1"
__author__ = "Danny O'Brien <http://www.spesh.com/danny/>"
__copyright__ = "Copyright Danny O'Brien"
__contributors__ = None
__license__ = "GPL v3"


from pywikipediabot import wikipedia
from datetime import date, timedelta
import re


def ordinal(value):
    """
    Converts zero or a *postive* integer (or their string
    representations) to an ordinal value.

    From here:
    http://code.activestate.com/recipes/576888-format-a-number-as-an-ordinal/

    """
    try:
        value = int(value)
    except ValueError:
        return value

    if value % 100 // 10 != 1:
        if value % 10 == 1:
            ordval = u"%d%s" % (value, "st")
        elif value % 10 == 2:
            ordval = u"%d%s" % (value, "nd")
        elif value % 10 == 3:
            ordval = u"%d%s" % (value, "rd")
        else:
            ordval = u"%d%s" % (value, "th")
    else:
        ordval = u"%d%s" % (value, "th")

    return ordval


def past_tuesday(today=date.today()):
    a_day = timedelta(days=1)
    future = today - a_day
    while (future.weekday() != 1):
        future -= a_day
    return future


def future_tuesday(today=date.today()):
    a_day = timedelta(days=1)
    future = today + a_day
    while (future.weekday() != 1):
        future += a_day
    return future


def next_ordinal(site, last_page):
    last_meeting = wikipedia.Page(site, last_page).get()

    last_count_search = re.search("The (\d\d+).. Meeting of Noisebridge",
            last_meeting)
    if last_count_search:
        last_count = int(last_count_search.group(1))
        last_count += 1
        return ordinal(last_count)
    else:
        return "XXXth"

def create_new_notes(site, last_page, next_page):
    template = wikipedia.Page(site, "Meeting_Notes_Template").get()
    template = re.sub("XXXth Meeting of Noisebridge",
            next_ordinal(site, last_page) + " Meeting of Noisebridge",
            template)
    future_page = wikipedia.Page(site, next_page)
    if future_page.exists():
        print "Already a page at " + next_page + " . Not overwriting."
    else:
        future_page.put(template, u"Secretaribot says its time for the "
                + next_ordinal(site, last_page) + " Noisebridge notes")

def redirect_pages(site, last_page, next_page):
    lm = wikipedia.Page(site, "last_meeting")
    nm = wikipedia.Page(site, "next_meeting")
    if lm.getRedirectTarget().title() != last_page:
        print "Redirecting [[Last_meeting]] to ", last_page
        lm.put("#REDIRECT [[%s]]" % last_page, "Secretaribot updating next meeting page")
    else:
        print "Last_meeting already points to correct page."
    if nm.getRedirectTarget().title() != next_page:
        print "Redirecting [[Next_meeting]] to ", next_page
        nm.put("#REDIRECT [[%s]]" % next_page, "Secretaribot updating for next meeting page")
    else:
        print "Next_meeting already points to correct page."

def main(args):
    site = wikipedia.Site("en")
    last_page = "Meeting Notes " + str(past_tuesday()).replace("-", " ")
    next_page = "Meeting Notes " + str(future_tuesday()).replace("-", " ")
    create_new_notes(site, last_page, next_page)
    redirect_pages(site, last_page, next_page)

import sys
import getopt


class Main():
    """ Encapsulates option handling. Subclass to add new options,
        add 'handle_x' method for an -x option,
        add 'handle_xlong' method for an --xlong option
        help (-h, --help) should be automatically created from module
        docstring and handler docstrings.
        test (-t, --test) will run all docstring and unittests it finds
        """
    class Usage(Exception):
        """ Use this to generate a Usage message """
        def __init__(self, msg):
            self.msg = msg

    def __init__(self):
        handlers = [i[7:] for i in dir(self) if i.startswith('handle_')]
        self.shortopts = ''.join([i for i in handlers if len(i) == 1])
        self.longopts = [i for i in handlers if (len(i) > 1)]

    def handler(self, option):
        i = 'handle_%s' % option.lstrip('-')
        if hasattr(self, i):
            return getattr(self, i)

    def default_main(self, args):
        print sys.argv[0], " called with ", args

    def handle_help(self, v):
        """ Shows this message """
        print sys.modules.get(__name__).__doc__
        descriptions = {}
        for i in list(self.shortopts) + self.longopts:
            d = self.handler(i).__doc__
            if d in descriptions:
                descriptions[d].append(i)
            else:
                descriptions[d] = [i]
        for d, opts in descriptions.iteritems():
            for i in opts:
                if len(i) == 1:
                    print '-%s' % i,
                else:
                    print '--%s' % i,
            print
            print d
        sys.exit(0)
    handle_h = handle_help

    def handle_test(self, v):
        """ Runs test suite for file """
        import doctest
        import unittest
        suite = unittest.defaultTestLoader.loadTestsFromModule(
                sys.modules.get(__name__))
        suite.addTest(doctest.DocTestSuite())
        runner = unittest.TextTestRunner()
        runner.run(suite)
        sys.exit(0)
    handle_t = handle_test

    def run(self, main=None, argv=None):
        """ Execute main function, having stripped out options and called the
        responsible handler functions within the class. Main defaults to
        listing the remaining arguments.
        """
        if not callable(main):
            main = self.default_main
        if argv is None:
            argv = sys.argv
        try:
            try:
                opts, args = getopt.getopt(argv[1:],
                        self.shortopts, self.longopts)
            except getopt.error, msg:
                raise self.Usage(msg)
            for o, a in opts:
                (self.handler(o))(a)
            return main(args)
        except self.Usage, err:
            print >>sys.stderr, err.msg
            self.handle_help(None)
            return 2

if __name__ == "__main__":
    sys.exit(Main().run(main) or 0)
