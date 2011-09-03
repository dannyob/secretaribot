#!/usr/bin/env python
##
# pywikipediabot.py
###
"""pywikipediabot.py

Looks for and loads the pywikipediabot library from environment variable
$PYWIKIBOT_DIR.

"""

__version__ = "0.1"
__author__ = "Danny O'Brien <http://www.spesh.com/danny/>"
__copyright__ = "Copyright Danny O'Brien"
__contributors__ = None
__license__ = "GPL v3"

import os
import sys
if 'PYWIKIBOT_DIR' in os.environ:
    sys.path.append(os.environ['PYWIKIBOT_DIR'])
try:
    import wikipedia
except ImportError:
    if 'PYWIKIBOT_DIR' in os.environ:
        print """
        ****
        Can't find Pywikipediabot libs (was looking in $PYWIKIBOT_DIR - %s)
        ****""" % os.environ["PYWIKIBOT_DIR"]
    else:
        print """
        ****
        Cannot find Pywikipediabot libraries. Suggest you check them out from
        http://pywikipediabot.sourceforge.net/ , then set PYWIKIBOT_DIR
        environment variable to point to their directory
        ****"""
    raise
