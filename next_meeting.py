#!/usr/bin/env python
##
# next_meeting.py
##
"""next_meeting.py

Creates the next meeting page from the template on the wiki. 
Calculates the next ordinal number for the meeting ie (the 31811th Meeting etc)

BUG: I think this will get confused if you run it too early (ie before Tuesday).

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

    >>> for i in range(1,13):
    ...     ordinal(i)
    ...     
    u'1st'
    u'2nd'
    u'3rd'
    u'4th'
    u'5th'
    u'6th'
    u'7th'
    u'8th'
    u'9th'
    u'10th'
    u'11th'
    u'12th'

    >>> for i in (100, '111', '112',1011):
    ...     ordinal(i)
    ...     
    u'100th'
    u'111th'
    u'112th'
    u'1011th'

    """
    try:
        value = int(value)
    except ValueError:
        return value

    if value % 100//10 != 1:
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
    while (future.weekday()!= 1):
        future -= a_day
    return future

def future_tuesday(today=date.today()):
    a_day = timedelta(days=1)
    future = today + a_day
    while (future.weekday()!= 1):
        future += a_day
    return future

def next_ordinal(site, last_page):
    last_meeting = wikipedia.Page(site, last_page).get()

    last_count_search = re.search("The (\d\d+).. Meeting of Noisebridge", last_meeting)
    if last_count_search:
        last_count = int(last_count_search.group(1))
        last_count += 1
        return ordinal(last_count)
    else:
        return "XXXth"

def main(args):
    site = wikipedia.Site("en")
    template = wikipedia.Page(site, "Meeting_Notes_Template").get()

    last_page = "Meeting_Notes_"+str(past_tuesday()).replace("-","_")
    next_page = "Meeting_Notes_"+str(future_tuesday()).replace("-","_")

    template = re.sub("XXXth Meeting of Noisebridge", next_ordinal(site, last_page)+" Meeting of Noisebridge", template)
    future_page = wikipedia.Page(site, next_page)
    if future_page.exists():
        print "Already a page at " + next_page + " Not attempting to overwrite."
    else:
        future_page.put( template, u"Secretaribot says its time for the " + next_ordinal(site, last_page) +" Noisebridge notes")

import sys
if __name__ == "__main__":
    sys.exit(main(sys.argv))

