#!/usr/bin/env python
##
# userlistpage.py
###
"""userlistpage.py

Utilities for getting lists of users from mediawiki installs

"""

__version__ = "0.1"
__author__ = "Danny O'Brien <http://www.spesh.com/danny/>"
__copyright__ = "Copyright Danny O'Brien"
__contributors__ = None
__license__ = "GPL v3"


from lxml import html
from lxml import cssselect

import unittest

import mechanize

import os

from pywikipediabot import wikipedia
import userlib
import urlparse


def user_list_since_user(site, lastUser):
    """ Maximum number of users = 2000 """
    return user_list_from_page("Special:ListUsers", site,
            '&username=%s&creationSort=1&limit=2000' % lastUser)


def user_list_from_page(page, site, query):
    url = urlparse.urljoin(site.siteinfo()['base'], site.get_address(page))
    f = url + "?" + query
    browser = mechanize.Browser()
    r = browser.open(f)
    return UserListPage(site, r)


class UserFromUserList(userlib.User):
    """ Subclassed wikipedia user.
    The href links to the user wiki page in a user list page have a class="new"
    attribute when there's no user page created yet. We use this fact to hint
    that some page don't have user pages without having to try and check
    via API."""

    def hadUserPage(self):
        if hasattr(self, 'user_page_exists'):
            return self.user_page_exists
        return True

    def forceUserPage(self, exist = True):
        self.user_page_exists = exist


class UserListPage:
    """ When fed a Wikipedia site and a mechanize response to a user list page,
    will parse and return a list of users. """
    def __init__(self, site, response):
        self.response = response
        self.lxml_root = html.parse(self.response).getroot()
        self.site = site

    def getUsers(self):
        ula = cssselect.CSSSelector('div.mw-spcontent > ul > li > a')
        list_links = ula(self.lxml_root)
        total_users = []
        for link in list_links:
            if 'User:' not in link.attrib['href']:
                continue
            new_user = UserFromUserList(self.site, link.text)
            total_users.append(new_user)
            if link.get('class') == 'new':
                new_user.forceUserPage(False)
            else:
                new_user.forceUserPage(True)
        return total_users


class UserListPageTest(unittest.TestCase):
    def setUp(self):
        self.noisebridge = wikipedia.Site('en')
        self.browser = mechanize.Browser()
        f = 'file://' + os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 't/index.php.htm'))
        self.r = self.browser.open(f)

    def test_canBeCreatedFromAMechanizeObject(self):
        up = UserListPage(self.noisebridge, self.r)
        self.assert_(up)
        return

    def test_canFindOneName(self):
        up = UserListPage(self.noisebridge, self.r)
        m = up.getUsers()
        self.assertGreaterEqual(len(m), 1)

    def test_canFindOneUser(self):
        up = UserListPage(self.noisebridge, self.r)
        self.assertIsInstance(up.getUsers()[0], userlib.User)

    def test_canFindSpecificUser(self):
        up = UserListPage(self.noisebridge, self.r)
        gu = up.getUsers()
        self.assertIn('Blackwing', [ i.name() for i in gu ] )

    def test_hasCorrectCountOfUsers(self):
        up = UserListPage(self.noisebridge, self.r)
        gu = up.getUsers()
        self.assertEquals(len(gu), 500)

    def test_canDiscoverWhoHasUserListPage(self):
        up = UserListPage(self.noisebridge, self.r)
        gu = up.getUsers()
        with_userpages = [i for i in gu if i.hadUserPage() ]
        without_userpages = [i for i in gu if not i.hadUserPage() ]
        self.assertTrue('Blackwing' in [i.name() for i in with_userpages])
        self.assertTrue('Blackwing' not in [i.name() for i in without_userpages])
        self.assertTrue('EmmaWatson0' in [i.name() for i in without_userpages])
        self.assertTrue('EmmaWatson0' not in [i.name() for i in with_userpages])
 

def main(args):
    """ FIXME put your command runner here """ 
    pass

import sys, getopt
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
        handlers  = [i[7:] for i in dir(self) if i.startswith('handle_') ]
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
        suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules.get(__name__))
        suite.addTest(doctest.DocTestSuite())
        runner = unittest.TextTestRunner()
        runner.run(suite)
        sys.exit(0)
    handle_t = handle_test

    def run(self, main= None, argv=None):
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
                opts, args = getopt.getopt(argv[1:], self.shortopts, self.longopts)
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

