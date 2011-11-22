# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE.
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: Manages an SQLite connection and performs merges between local database and calendar
# and blogs.

import datetime
import logging
import pprint
import sqlite3
import time

import blogger
import gcal

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

  def update(self, events, posts):
    """Updates a DataStore with new events and news.

    Args:
      events: A list of gcal.Event
      posts: A list of blogger.Post"""

    feed_events = dict([(e.event_id, e.updated) for e in events])
    query = ("select id, updated from events where id in (" +
             ", ".join([repr(e) for e in feed_events.iterkeys()]) + ")")
    self.c.execute(query)
    already_have_events = dict(self.c.fetchall())
    new_events = set(feed_events.keys()) - set(already_have_events.keys())


    rss_post_ids = dict([(post.id, post.updated) for post in posts])
    query = ("select id, updated from posts where id in (" +
             ", ".join([repr(id) for id in rss_post_ids]) + ")")
    self.c.execute(query)
    already_have_posts = dict(self.c.fetchall())
    new_posts = set(rss_post_ids.keys()) - set(already_have_posts.keys())

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
          # logging.warning("Not modifying event %s" % event.event_id)
          continue
        else:
          # Must be a modified event... need to update database.
          logging.warning("Updating event %s (%s -> %s)" % (
              event.event_id,
              already_have_events[event.event_id], event.updated))
          self.c.execute("update events set updated=?, calendar_title=?, event_title=?, "
                         "start_time=?, end_time=?, location=?, status=?, description=?, "
                         "is_all_day=?, thumbnail=?, full_image=? "
                         "where id=?",
                         (event.updated, event.calendar_title, event.event_title,
                          ToTimestamp(event.start_time), ToTimestamp(event.end_time), event.location,
                           event.status, event.description, int(event.is_all_day),
                           event.thumbnail, event.full_image, event.event_id))
      else:
        # Must be a new event!
        logging.warning("New event %s" % event.event_id)
        self.c.execute("insert into events values (?,?,?,?,?,?,?,?,?,?,?,?)",
                       (event.event_id, event.updated, event.calendar_title, event.event_title,
                        ToTimestamp(event.start_time), ToTimestamp(event.end_time), event.location,
                        event.status, event.description, int(event.is_all_day), event.thumbnail,
                        event.full_image))
    for post in posts:
      if post.id in already_have_posts:
        if already_have_posts[post.id] == post.updated:
          continue
        else:
          logging.warning("Updating post %s (%r -> %r)" % (
              post.id, already_have_posts[post.id], post.updated))
          self.c.execute("update posts set updated=?, title=?, published=?, content=?, "
                         "categories=?, summary=? "
                         "where id=?",
                        (post.updated, post.title, ToTimestamp(post.published),
                         post.content, post.categories, post.summary, post.id))
      else:
       logging.warning("New post %s" % post.id)
       self.c.execute("insert into posts values (?, ?, ?, ?, ?, ?, ?)",
                      (post.id, post.updated, post.title, ToTimestamp(post.published),
                       post.content, post.categories, post.summary))

  def CreateEventsFromResults(self):
    for row in self.c:
      e = gcal.Event(event_id=row[0], updated=row[1], calendar_title=row[2],
                     event_title=row[3], start_time=datetime.datetime.fromtimestamp(row[4]),
                     end_time=datetime.datetime.fromtimestamp(row[5]),
                     location=row[6] or "", status=row[7], description=row[8] or "",
                     is_all_day=bool(row[9]), thumbnail=row[10] or None, full_image=row[11] or None)
      if e.status != "canceled":
        yield e

  def GetEventsInRange(self, start_date, end_date):
    """Returns a list of events in the date range, inclusive."""
    self.c.execute("select * from events where start_time >= ? and start_time <= ? order by start_time",
                    (ToTimestamp(start_date), ToTimestamp(end_date)))
    return self.CreateEventsFromResults()


  def GetAllEvents(self):
    """Returns all of the events, inclusive, for archival purposes."""
    self.c.execute("select * from events order by start_time")
    return self.CreateEventsFromResults()


  def CreatePostsFromResults(self):
    for row in self.c:
      p = blogger.Post(id=row[0], updated=row[1],
                       title=row[2], published=datetime.datetime.fromtimestamp(row[3]),
                       content=row[4], categories=row[5], summary=row[6])
      yield p

  def GetAllPosts(self):
    """Returns all of the posts, inclusive, for archival purposes."""
    self.c.execute("select * from posts order by published desc")
    return self.CreatePostsFromResults()


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
