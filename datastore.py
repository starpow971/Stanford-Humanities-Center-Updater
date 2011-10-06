# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: Dump events from calendar and tumblr feeds straight into database.

import logging
import sqlite3
import time

class DataStore:
	"""DataStore manages the SQLite3 connection."""
	
	def __init__(self, filename):
		"""Construct a DataStore.
		
		Establishes a connection to the named database and constructs a cursor.
		
		Args:
			filename: A string naming an SQLite3 database.
			
		Returns:
			A new DataStore object."""
		self.conn = sqlite3.connect(filename)
		self.c = self.conn.cursor()

	def update(self, events, news):		
		"""Updates a DataStore with new events and news.
		
		Args:
			events: A list of gcal.Event
			news: A list of tumblr.Post"""
			
		feed_event_ids = set([e.event_id for e in events])
		query = ("select id from events where id in (" +
						 ", ".join([repr(e) for e in feed_event_ids]) + ")")
		self.c.execute(query)
		already_have_events = set([row[0] for row in self.c.fetchall()])
		new_events = feed_event_ids - already_have_events
		logging.warning("new_events = %r" % new_events)
		
		
		rss_post_ids = set([p.post_id for p in news])
		query = ("select id from news where id in (" +
						 ", ".join([str(id) for id in rss_post_ids]) + ")")
		self.c.execute(query)
		already_have_posts = set([row[0] for row in self.c.fetchall()])
		new_posts = rss_post_ids - already_have_posts
		logging.warning("new_posts = %r" % new_posts)
		return
			
		for event in events:
			if event.event_id in already_have_events:
				continue
			self.c.execute("insert into events values (?,?,?,?,?,?,?,?)", 
										 (event.event_id, event.calendar_title, event.event_title,
								 			ToTimestamp(event.start_time), ToTimestamp(event.end_time), event.location,
								 			event.location, event.description))
		for post in news:
			if post.post_id in already_have_posts:
				continue
			self.c.execute("insert into news values (?, ?, ?, ?, ?)",
										 (post.post_id, post.post_title, ToTimestamp(post.post_date), post.post_content,
										  post.post_category))
								
	def save(self):
		"""Commits pending changes to the database."""
		self.conn.commit()
						
	def close(self):
		"""Close the database.  Don't call any more methods after this."""
		self.c.close()


def ToTimestamp(d):
	"""Converts a datetime to a unix timestamp.
	
	Args:
		d: a datetime.datetime object.
		
	Returns:
		An integer representing a unix timestamp."""
	# STUPID PYTHON!!
	return int(time.mktime(d.timetuple()))
	
def load(filename):
	"""Convenience function for creating a DataStore."""
	return DataStore(filename)