# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: Dump events from calendar and tumblr feeds straight into database.

import sqlite3
import time
import urllib2

import gcal
import tumblr

events = gcal.parse_feed(urllib2.urlopen("https://www.google.com/calendar/feeds/stanford.humanities.events%40gmail.com/public/basic?showdeleted=true"))
news = tumblr.parse_rss(urllib2.urlopen("http://stanfordhumanitiescenter.tumblr.com/rss"))

def ToTimestamp(d):
	# STUPID PYTHON!!
	return int(time.mktime(d.timetuple()))

conn = sqlite3.connect("database.db")
c = conn.cursor()
for event in events:
	c.execute("insert into events values (?,?,?,?,?,?,?,?)", 
						(event.event_id, event.calendar_title, event.event_title,
						 ToTimestamp(event.start_time), ToTimestamp(event.end_time), event.location,
						 event.location, event.description))
for post in news:
	c.execute("insert into news values (?, ?, ?, ?)",
						(post.post_title, ToTimestamp(post.post_date), post.post_content, post.post_category))
						
conn.commit()
c.close()