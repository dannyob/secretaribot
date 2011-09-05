<blockquote>
"Go away or I will replace you with a very small shell script"
</blockquote>

[Secretaribot](https://www.noisebridge.net/wiki/Secretaribot) is actually a few (quite small) python scripts, which, along with [Noisebot](https://www.noisebridge.net/wiki/Noisebot), help out the Noisebridge collective with housekeeping tasks.

This document is automagically created by make.py and README.intro in the
Secretaribot repository at [github](https://github.com/dannyob/secretaribot),
which is written out to the [Secretaribot's
page](https://www.noisebridge.net/wiki/Secretaribot) on the Noisebridge wiki. 

### death_to_wikispammers ###

Usage: death_to_wikispammers [username]
Downloads a list of recently created users, starting at the username given.
One by one, shows their user page via STDOUT.
Delete user page and block for spam? it asks, [y/n]
If yes, deletes user page, blocks user for spamming
If no, goes onto next

### make_readme.py ###

Meta-helper script to write the README in this directory to the Secretaribot page on the NB wik.

### merge_blocked_users.py ###

Merge (and then delete) all blocked users into a single, uber-spam account.

'And nothing of value was lost'

### next_meeting.py ###

Creates the next meeting page from the template on the wiki.
Calculates the next ordinal number for the meeting ie (the 31811th Meeting etc)

### pywikipediabot.py ###

Looks for and loads the pywikipediabot library from environment variable
$PYWIKIBOT_DIR.

### userlistpage.py ###

Utilities for getting lists of users from mediawiki installs

### www_watch.py ###

Goes out and checks a Wikipedia table full of links, and saves the etags from
the headers; by updating these etags on the page, it will trigger a mediawiki
page change whenever any of the other pages change. If you watch that page,
you'll be effectively watching all the other external pages.

### arooga.agi - call a bunch of people to 311 conf call ###

Usage: /etc/asterisk/agi-bin/arooga.cgi

Called by Asterisk dialplan, extracts callerid safely,
sends it onto an email alias, records info in syslog.
