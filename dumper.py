#!/usr/bin/env python
# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE.
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: Dump events from calendar and tumblr feeds straight into database.

import cStringIO
import threading
import urllib2

import blogger
import datastore
import config
import gcal
import tumblr


class FetchThread(threading.Thread):
  """A worker thread that fetches a url."""
  def __init__(self, url):
    threading.Thread.__init__(self, name="Url fetcher for url %s" % url)
    self.url = url
    self.document = None

  def run(self):
    # Force the url library to read the whole document.
    self.document = cStringIO.StringIO(urllib2.urlopen(self.url).read())


def main():
  gcal_template = (
      "http://www.google.com/calendar/feeds/%s/public/basic?"
      "showdeleted=true&updated-min=2011-08-01T01:00:00-08:00&max-results=1000")
  threads = [FetchThread(gcal_template % cal_id)
             for cal_id in config.calendar_ids.itervalues()]
  map(FetchThread.start, threads)  # Do work.
  map(FetchThread.join, threads)  # Wait for work to end.
  events = []
  for t in threads:
    events.extend(gcal.parse_feed(t.document))

  posts = blogger.GetPosts()

  store = datastore.load("database.db")
  store.update(events, posts)
  store.save()
  store.close()

if __name__ == '__main__':
  main()
