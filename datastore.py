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
      
    feed_events = dict([(e.event_id, e.updated) for e in events])
    query = ("select id, updated from events where id in (" +
             ", ".join([repr(e) for e in feed_events.iterkeys()]) + ")")
    self.c.execute(query)
    already_have_events = dict(self.c.fetchall())
    new_events = set(feed_events.keys()) - set(already_have_events.keys())
    
    
    rss_post_ids = set([p.post_id for p in news])
    query = ("select id from news where id in (" +
             ", ".join([str(id) for id in rss_post_ids]) + ")")
    self.c.execute(query)
    already_have_posts = set([row[0] for row in self.c.fetchall()])
    new_posts = rss_post_ids - already_have_posts
    logging.warning("new_posts = %r" % new_posts)
    
    # NOTE(scottrw): There are four cases to consider:
    # 1. old event not in feed. No action required from us, do nothing.
    # 2. new event. Feed event id is not in database. Insert event into database.
    # 3. unmodified event. Feed event id is in database, and updated fields are equal. Do nothing.
    # 4. modified event. Feed event id is in database, but updated fields are unequal. Update database.
      
    for event in events:
      if event.event_id in already_have_events:
        # Hm, event id is present in the feed and the database. Could be case 3 OR 4.
        if already_have_events[event.event_id] == event.updated:
          # Aha, an unmodified event!
          logging.warning("Not modifying event %s" % event.event_id)
          continue
        else:
          # Must be a modified event... need to update database.
          logging.warning("Updating event %s" % event.event_id)
          self.c.execute("update events set updated=?, calendar_title=?, event_title=?, "
                         "start_time=?, end_time=?, location=?, status=?, description=? "
                         "where id=?",
                         (event.updated, event.calendar_title, event.event_title,
                          ToTimestamp(event.start_time), ToTimestamp(event.end_time), event.location,
                           event.status, event.description, event.event_id))
      else:
        # Must be a new event!
        logging.warning("New event %s" % event.event_id)
        self.c.execute("insert into events values (?,?,?,?,?,?,?,?,?)", 
                       (event.event_id, event.updated, event.calendar_title, event.event_title,
                        ToTimestamp(event.start_time), ToTimestamp(event.end_time), event.location,
                        event.status, event.description))
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