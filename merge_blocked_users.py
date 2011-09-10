#!/usr/bin/env python
##
# merge_blocked_users.py
###
"""merge_blocked_users.py

Merge (and then delete) all blocked users into a single, uber-spam account.

'And nothing of value was lost'

"""

__version__ = "0.1"
__author__ = "Danny O'Brien <http://www.spesh.com/danny/>"
__copyright__ = "Copyright Danny O'Brien"
__contributors__ = None
__license__ = "GPL v3"

from pywikipediabot import wikipedia
import userlistpage
import userlib


def mergeUser(site, olduser, newuser, delete=False):
    predata = {}
    predata['olduser'] = olduser.username
    predata['newuser'] = newuser.username
    if predata['olduser'] == predata['newuser']:
        return (False, False)
    if delete:
        predata['deleteuser'] = "1"
    else:
        predata['deleteuser'] = "0"
    predata['token'] = site.getToken(sysop=True)

    (r, text) = site.postForm('/wiki/Special:UserMerge', predata, sysop=True)
    if ('Merge from' in text) and ('is complete' in text):
        merge_succeed = True
    else:
        merge_succeed = False
    if ('has been deleted' in text):
        delete_succeed = True
    else:
        delete_succeed = False
    return (merge_succeed, delete_succeed)


def main(args):
    if not args:
        initial_user = "SpammerHellDontDelete"
    else:
        initial_user = args[0]

    nb = wikipedia.Site('en', "noisebridge")
    spam_user = userlib.User(nb, "SpammerHellDontDelete")

    ul = userlistpage.user_list_since_user(nb, initial_user).getUsers()
    for i in ul:
        print i
        if i.isBlocked():
            print "Merging", i
            (merged, deleted) = mergeUser(nb, i, spam_user, delete=True)
            print "Merged:", merged
            print "Deleted:", deleted


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
