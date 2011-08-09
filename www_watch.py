#!/usr/bin/env python
##
# www_watch.py
###
"""www_watch.py

Goes out and checks a Wikipedia table full of links, and saves the etags from
the headers; by updating these etags on the page, it will trigger a mediawiki
page change whenever any of the other pages change. If you watch that page,
you'll be effectively watching all the other external pages.

"""

__version__ = "0.1"
__author__ = "Danny O'Brien <http://www.spesh.com/danny/>"
__copyright__ = "Copyright Danny O'Brien"
__contributors__ = None
__license__ = "GPL v3"

import unittest2 as unittest
import os
import urllib2
import hashlib
import re
from pywikipediabot import wikipedia


def etag(f):
    if 'etag' in f.headers.keys():
        return f.headers['etag']
    return hashlib.md5(f.read()).hexdigest()

def last_modified(f):
    if 'last-modified' in f.headers.keys():
        return f.headers['last-modified']
    return "Unknown"

class WikiTable():
    @classmethod
    def _stringify(c, rows, header, fields, real_fields):
        """ Creates a Wiki markup table from a list of rows. The fields
        parameter lists the keys used in the rows, the real_fields list the
        readable name at the top of the table. The two lists should map onto
        each other, and be in the order of the columns."""

        s = header + '\n'
        s += "|-\n"
        for f in real_fields:
            s += "!" + f + '\n'
        for r in rows:
                s += "|-\n"
                row = []
                for k in r:
                    pos = fields.index(k)
                    row.append( (pos, r[k]) )
                row.sort(key=lambda s: s[0])
                s += '\n'.join(['| '+r for (num, r) in row])
        s += "\n|}"
        return s


    def __init__(self, wikimarkup):
        self.wikimarkup = wikimarkup

    def wiki_to_dict(self):
        tablemarkup = self.wikimarkup.split('\n')

        fields = []
        real_fields = []
        rows = []
        column = 0
        row = {}
        state = 'INIT'
        for l in tablemarkup:
            z = l.strip()
            if z.startswith('{|'):
                state = 'IN_TABLE'
                self.header = z
            if z.startswith('!') and (state == 'NEW_ROW'):
                real_field = z[1:]
                field = real_field.strip().lower()
                field = re.sub('[^a-z]','-', field)
                fields.append(field)
                real_fields.append(real_field)
            if z.startswith('|-'):
                state = 'NEW_ROW'
                if row:
                    rows.append(row)
                continue
            if z.startswith('|}'):
                if row:
                    rows.append(row)
                break
            if z.startswith('|') and (state == 'NEW_ROW'):
                column = 0
                row = {}
                state = 'IN_ROW'
            if z.startswith('|') and (state == 'IN_ROW'):
                value = z[1:].strip()
                row[fields[column]] = value
                column += 1
        self.real_fields = real_fields
        self.fields = fields
        self.rows = rows
        return self.rows

    def __str__(self):
        self.wiki_to_dict()
        return WikiTable._stringify(self.rows, self.header, self.fields, self.real_fields)

    def copy_with_new_dict(self, d):
        self.wiki_to_dict()
        return WikiTable(WikiTable._stringify(d, self.header, self.fields, self.real_fields))
        
class WikiTableConversions(unittest.TestCase):
    def setUp(self):
        self.mup = '''{| class="wikitable"
|-
! URL
! Etag
! Last Modified
|-
| http://packages.debian.org/changelogs/pool/main/m/mediawiki-extensions/mediawiki-extensions_2.4/changelog
| foo
| bar
|}'''
        self.wikitext = WikiTable(self.mup)

    def test_can_extract_headers_from_wikimarkup(self):
        b = self.wikitext.wiki_to_dict()
        self.assertIn('url', b[0].keys())
        self.assertIn('etag', b[0].keys())
        self.assertIn('last-modified', b[0].keys())

    def test_can_extract_a_row_from_wikimarkup(self):
        b = self.wikitext.wiki_to_dict()
        self.assertEquals(b[0]['url'],'http://packages.debian.org/changelogs/pool/main/m/mediawiki-extensions/mediawiki-extensions_2.4/changelog')
        self.assertEquals(b[0]['etag'],'foo')
        self.assertEquals(b[0]['last-modified'],'bar')

    def test_can_return_string_of_markup(self):
        self.assertEqual(self.mup,str(self.wikitext))

        
    def test_can_reconstruct_markup_from_dict(self):
        b = self.wikitext.wiki_to_dict()
        b[0]['url'] = 'blah'
        changed = '''{| class="wikitable"
|-
! URL
! Etag
! Last Modified
|-
| blah
| foo
| bar
|}'''
        c = self.wikitext.copy_with_new_dict(b)
        self.assertEquals(str(c), changed)

class ReturnAnETag(unittest.TestCase):
    def setUp(self):
        self.f1 = 'file://' + os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),'t/non-identical-file1.html'))
        self.f2 = 'file://' + os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),'t/non-identical-file2.html'))

    def test_shouldReturnAValidEtag(self):
        m = urllib2.urlopen(self.f1)
        m.headers['ETag']='dead-beef-dead-beef'
        self.assertEquals(etag(m), 'dead-beef-dead-beef')

    def test_shouldMakeUpEtagFromContent(self):
        m = urllib2.urlopen(self.f1)
        self.assertIsNotNone(etag(m))

    def test_fakeEtagShouldChangeWithContent(self):
        m1 = urllib2.urlopen(self.f1)
        m2 = urllib2.urlopen(self.f2)
        etag1 = etag(m1)
        etag2 = etag(m2)
        self.assertNotEqual(etag1,etag2)

    def test_shouldReturnAValidLastModified(self):
        m = urllib2.urlopen(self.f1)
        self.assertNotEqual(last_modified(m), 'Unknown')

    def test_shouldReturnAnUnknownLastModified(self):
        m = urllib2.urlopen(self.f1)
        del m.headers['last-modified']
        self.assertEquals(last_modified(m), 'Unknown')

import copy
def main(args):
    site = wikipedia.getSite('en')
    watch_list_page = wikipedia.Page(site, 'Secretaribot/Watchlist')
    markup = watch_list_page.get()
    wt = WikiTable(markup)
    urls = wt.wiki_to_dict()
    new_urls = copy.deepcopy(urls)
    for i in new_urls:
        this_url = i['url']
        url_connection = urllib2.urlopen(this_url)
        i['etag'] = etag(url_connection)
        i['last-modified'] = last_modified(url_connection)
    wt2 = wt.copy_with_new_dict(new_urls)
    if str(wt2) != str(wt):
        watch_list_page.put(str(wt2), comment="www_watch spotted a page change")


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

