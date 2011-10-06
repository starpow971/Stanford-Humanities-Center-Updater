# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: Dump events from calendar and tumblr feeds straight into database.

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
		
		TODO: Don't duplicate existing news and events.
		
		Args:
			events: A list of gcal.Event
			news: A list of tumblr.Post"""
		for event in events:
			self.c.execute("insert into events values (?,?,?,?,?,?,?,?)", 
										 (event.event_id, event.calendar_title, event.event_title,
								 			ToTimestamp(event.start_time), ToTimestamp(event.end_time), event.location,
								 			event.location, event.description))
		for post in news:
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