# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: Dump events from calendar and tumblr feeds straight into database.


import urllib2

import datastore
import gcal
import tumblr

events = gcal.parse_feed(urllib2.urlopen("https://www.google.com/calendar/feeds/stanford.humanities.events%40gmail.com/public/basic?showdeleted=true&updated-min=2011-09-26T01:00:00-08:00&max-results=1000"))
news = tumblr.parse_rss(urllib2.urlopen("http://stanfordhumanitiescenter.tumblr.com/rss"))

store = datastore.load("database.db")
store.update(events, news)
store.save()
store.close()
