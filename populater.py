#!/usr/bin/env python
# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE.
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: Pulls events from database and writes them to disc.


from Cheetah.Template import Template
from lxml import etree
from pprint import pprint
from optparse import OptionParser
from StringIO import StringIO
from dateutil import rrule
import bisect
import collections
import datetime
import re
import sys

import datastore
import config
import file_manager

# TODO: Figure out why it creates pages with no events (per month calendars).
# TODO: Remove workshop events from Events Calendar.
# Known issues:
# Doesn't line break in event descriptions. (I thought we had fixed that?)
# Creates pages with no events- if another calendar has events in those months. Workshop landing page only?
# Title not displaying correctly. Displays "Event Calendar" or "Workshop Calendar" all the time.
# Per Month Landing Cals: "Events For March 2012" or "Workshop Events For 2012"
# Per Month Indiv Cals: "Stanford Humanities Center Events For March 2012"
# Indiv Cals landing: "Stanford Humanities Center Events", "Archaeology Today Calendar"
# In the middle of a month, forward and back link to the current month. Solvable problem? Change language
# to match landing pages: "All events for"

class PostFlipBook:
  """Sets up the flipbooks for posts- yearmonths, tags, all posts."""
  def __init__(self, uri="", pretty_name=""):
    self.uri = uri
    self.pretty_name = pretty_name
    self.posts = []

  def render(self, fm, options):
    groups = group(self.posts, 10)
    pagenums = range(len(groups))
    pages = zip([None] + pagenums[:-1], pagenums, pagenums[1:] + [None], groups)
    for next_pg_num, current_pg_num, back_pg_num, posts in pages:
      fm.save(options.output_dir + self.page_uri(current_pg_num), str(Template(file="news-template.tmpl",
              searchList=[{"posts" : posts,
                           "pretty_name": self.pretty_name,
                           "forward_url": self.page_uri(next_pg_num),
                           "forward_text": "Newer Posts&raquo;",
                           "back_url": self.page_uri(back_pg_num),
                           "back_text": "Older Posts"}])))

  def page_uri(self, current_pg_num):
    if current_pg_num is None:
      return None
    if current_pg_num == 0:
      return self.uri
    else:
      path, extension = self.uri.rsplit(".", 1)
      return path + "-" + str(current_pg_num) + "." + extension

class FlipbookIndex:
  def __init__(self, yearmonth, categories):
    self.yearmonth = yearmonth
    self.categories = categories

def group(lst, n):
  return zip(*[lst[i::n] for i in range(n)])

def parse_args(argv):
  """Sets up the option parser and parses command line arguments.

  Returns:
    options, args: a pair whose first element is an Options object with settings
    taken from the command line, and whose second element is the remaining
    unparsed arguments on the command line.
  """
  op = OptionParser()
  op.add_option("-o", "--output-dir", dest="output_dir",
                help="Output generated files under DIR",
                metavar="DIR",
                default="/Library/Server/Web/Data/Sites/Default/")
  op.add_option("-t", "--test-date", dest="test_date",
                action="store_true",
                help="Force the date to 2012-01-31 for testing",
                default=False)
  options, args = op.parse_args(argv[1:])
  if not options.output_dir.endswith("/"):
    options.output_dir += "/"
  return options, args


def main(argv):
  options, args = parse_args(argv)
  fm = file_manager.FileManager()
  ds = datastore.DataStore("database.db")

  now = datetime.datetime.now()
  if options.test_date:
    now = datetime.datetime(2012, 01, 31, 8, 25)
  end_date = now + datetime.timedelta(31)

  all_events = CalendarFlipBook(calendar_name="Events Calendar",
                                landing_page_template="calendar-landing-page.tmpl",
                                landing_page_uri="events/calendar/index.html",
                                title_prefix="Events")
  all_workshops = CalendarFlipBook(calendar_name="Workshop Calendar",
                                   landing_page_template="workshop-landing-page.tmpl",
                                   landing_page_uri="workshops/calendar/index.html",
                                   title_prefix="Workshop Events")

  flipbooks = {} #calendar_name -> flipbook
  #fix calendar_name and template.
  for c in config.calendar_ids:
    if c.calendar_name in ("Stanford Humanities Center Events",
                           "Co-sponsored Events Held at the Humanities Center",
                           "Test SHC Calendar"):
      landing_page_uri="events/calendar/%s.html" % friendly_title(c.calendar_name)
    else:
      landing_page_uri="workshops/calendar/%s.html" % friendly_title(c.calendar_name)
    flipbooks[c.calendar_name] = CalendarFlipBook(calendar_name=c.calendar_name,
                                                  title_prefix=c.calendar_name + " Events",
                                                  landing_page_template=c.landing_page_template,
                                                  landing_page_uri=landing_page_uri)
  calendars = [all_events, all_workshops] + flipbooks.values()

  events = list(ds.GetAllEvents())
  for event in events:
    all_events.AddEvent(event, now, end_date)
    all_workshops.AddEvent(event, now, end_date)
    flipbooks[event.calendar_title].AddEvent(event, now, end_date)

  for calendar in calendars:
    calendar.WriteUpcomingEvents(options, fm, calendars, now)
    calendar.WritePerMonthCalendars(options, fm, calendars)
    calendar.WritePerDayCalendars(options, fm, calendars)
    calendar.WriteMiniCals(options, fm)

  WriteEventPages(options, fm, events, calendars)  # Move me last

  all_posts = list(ds.GetAllPosts())
  WritePostPages(options, fm, all_posts)
  all_posts_fb = PostFlipBook("news-videos/news/index.html", "All Posts")
  for post in all_posts:
    all_posts_fb.posts.append(post)
  all_posts_fb.render(fm, options)

  if options.test_date:
    SanityCheck(fm, options)

  #print fm.show_diff()
  fm.commit()

def MyAssert(actual, expected):
  assert actual == expected, "Got %r" % actual


class CalendarFlipBook:
  def __init__(self, landing_page_template="", calendar_name="", title_prefix="",
               landing_page_uri=""):
    self.landing_page_template = landing_page_template
    self.calendar_name = calendar_name
    self.title_prefix = title_prefix
    self.landing_page_uri = landing_page_uri
    self.events = {}  # month -> [event]
    self.daily_events = {} # day -> [event]
    self.upcoming = []
    self.next_date = None
    self.back_date = None
    self.earliest_date = None
    self.latest_date = None

  def __repr__(self):
    return "<Calendar %r>" % self.calendar_name

  def WriteMiniCals(self, options, fm):
    if self.earliest_date is None or self.latest_date is None:
      return
    first_day = datetime.datetime(self.earliest_date.year,
                                  self.earliest_date.month,
                                  1)
    # NOTE(scottw): weekday() is the ISO weekday, where Monday is day 0. That's stupid, so we have
    # to perform some modular arithmetic to get the days to work out correctly.
    first_weekday = (first_day.weekday() + 1) % 7

    # The last day is the first day of the month after the month containing self.latest_date
    last_day = datetime.datetime(self.latest_date.year + 1, 1, 1)

    # First, fill out a flat list of days in the range (first_day, last_day]
    days = [None] * first_weekday  # Pad with None up to first weekday
    current_day = first_day
    while current_day < last_day:
      days.append(current_day)
      current_day += datetime.timedelta(days=1)
    days_in_last_week = len(days) % 7
    days_of_padding = (7 - days_in_last_week) % 7
    days.extend([None] * days_of_padding)   # Add trailing None to come to exactly a week's worth
    assert len(days) % 7 == 0, "There should be an even multiple of 7 days!"

    month_starts = {}
    for num, day in enumerate(days):
      if not day:
        continue
      month = datetime.datetime(day.year, day.month, 1)
      if month not in month_starts:
        month_starts[month] = num / 7

    months = month_starts

    # Divide up the day list into weeks
    weeks = []
    for week in range(len(days) / 7):
      sunday = week * 7
      saturday = sunday + 7
      weeks.append(days[sunday:saturday])

    years = {}
    for month in months:
      years.setdefault(month.year, []).append(month)

    month_dates = sorted(months.keys())
    for prev_month, month, next_month in zip([None] + month_dates[:-1],
                                             month_dates,
                                             month_dates[1:] + [None]):
      fm.save(options.output_dir + self.minical_uri(month),
              str(Template(file="minical.tmpl",
                         searchList=[{"weeks" : weeks[months[month]:months[month] + 6],
                                      "daily_events": self.daily_events,
                                      "month": month,
                                      "years": years,
                                      "prev_month": prev_month,
                                      "next_month": next_month,
                                      "minical_uri": self.minical_uri,
                                      "day_uri": self.day_uri
                                      }])))

  def WriteUpcomingEvents(self, options, fm, calendars, today):
    forward_url = self.next_date and "../../" + self.month_uri(self.next_date)
    forward_text = forward_url and self.next_date.strftime('%b %Y') + "&raquo;"
    back_url = self.back_date and "../../" + self.month_uri(self.back_date)
    back_text = back_url and self.back_date.strftime('%b %Y')
    minical_uri = "../../" + self.minical_uri(today)
    # TESTING CODE
    # fm.save(options.output_dir + self.minical_uri(today), "I'm a minical for %r" % today)

    fm.save(options.output_dir + self.landing_page_uri,
            str(Template(file=self.landing_page_template,
                         searchList=[{"events": self.upcoming,
                                      "calendar_title": self.calendar_name,
                                      # TODO(chris): Change the template calendar_urls to calendars.
                                      # in the template:
                                      #   #for calendar in calendars
                                      #     <a href="$calendar.uri()">$calendar.calendar_name</a>
                                      #   #end
                                      "calendar_urls": [(c.calendar_name, self.landing_page_uri) for c in calendars],
                                      "forward_url": forward_url,
                                      "forward_text": forward_text,
                                      "back_url": back_url,
                                      "back_text": back_text,
                                      "minical_uri": minical_uri}])))

  def WritePerMonthCalendars(self, options, fm, calendars):
    month_events = sorted(self.events.items())
    months = [month for month, events in month_events]
    for (yearmonth, events), back, forward in zip(month_events,
                                                  [None] + months[:-1],
                                                  months[1:] + [None]):
      per_month_name = self.calendar_name + yearmonth.strftime(": %B %Y")
      minical_uri = "../../" + self.minical_uri(yearmonth)
      # fm.save(options.output_dir + self.minical_uri(yearmonth), "I'm a minical for %r" % yearmonth)
      fm.save(options.output_dir + self.month_uri(yearmonth),
              str(Template(file=self.landing_page_template,
                            searchList=[{"events": events,
                                        "calendar_urls": [(c.calendar_name, c.landing_page_uri) for c in calendars],
                                        "calendar_title": per_month_name,
                                        "back_url": back and "../../" + self.month_uri(back),
                                        "back_text": back and back.strftime ('%b %Y'),
                                        "forward_url": forward and "../../" + self.month_uri(forward),
                                        # TODO(chris): Put &raquo; in the template
                                        "forward_text": forward and forward.strftime('%b %Y') + "&raquo;",
                                        "minical_uri": minical_uri}])))

  def WritePerDayCalendars(self, options, fm, calendars):
    for day, events in self.daily_events.iteritems():
      per_day_name = self.calendar_name + day.strftime(": %B %d, %Y")
      minical_uri = "../../" + self.minical_uri(day) + "#day:" + day.strftime('%d %b %Y')
      fm.save(options.output_dir + self.day_uri(day),
              str(Template(file=self.landing_page_template,
                            searchList=[{"events": events,
                                        "calendar_urls": [(c.calendar_name, c.landing_page_uri) for c in calendars],
                                        "calendar_title": per_day_name,
                                        "back_url": None,
                                        "back_text": None,
                                        "forward_url": None,
                                        "forward_text": None,
                                        "minical_uri": minical_uri}])))

  def AddEvent(self, event, now, end_date):
    month = datetime.datetime(event.start_time.year, event.start_time.month, 1)
    if month not in self.events:
      self.events[month] = []
    self.events[month].append(event)

    day = datetime.datetime(event.start_time.year, event.start_time.month, event.start_time.day)
    if day not in self.daily_events:       # if k in a
      self.daily_events[day] = []
    self.daily_events[day].append(event)

    self.latest_date = max(self.latest_date or event.start_time, event.start_time)
    self.earliest_date = min(self.earliest_date or event.start_time, event.start_time)
    if event.start_time >= now and event.start_time <= end_date:
      self.upcoming.append(event)
    if event.start_time < now:
      self.back_date = max(self.back_date or event.start_time, event.start_time)
    if event.start_time > end_date:
      self.next_date = min(self.next_date or event.start_time, event.start_time)


  def month_uri(self, yearmonth):
    if self.calendar_name == "Events Calendar":
      return yearmonth.strftime("events/calendar/%Y-%m.html")
    if self.calendar_name == "Workshop Calendar":
      return yearmonth.strftime("workshops/calendar/%Y-%m.html")
    else:
      return yearmonth.strftime("events/calendar/%%Y-%%m-%s.html" % friendly_title(self.calendar_name))

  def day_uri(self, day):
    if self.calendar_name == "Events Calendar":
      return day.strftime("events/calendar/%Y-%m-%d.html")
    if self.calendar_name == "Workshop Calendar":
      return day.strftime("workshops/calendar/%Y-%m-%d.html")
    else:
      return day.strftime("events/calendar/%%Y-%%m-%%d-%s.html" % friendly_title(self.calendar_name))

  def minical_uri(self, yearmonth):
    if self.calendar_name == "Events Calendar":
      return yearmonth.strftime("events/calendar/%Y-%m.mini.html")
    if self.calendar_name == "Workshop Calendar":
      return yearmonth.strftime("workshops/calendar/%Y-%m.mini.html")
    else:
      return yearmonth.strftime("events/calendar/%%Y-%%m-%s.mini.html" % friendly_title(self.calendar_name))

def friendly_title(calendar_name):
  title = re.sub(" +", "-", calendar_name.lower())
  title = re.sub("[^-a-z0-9]", "", title)
  return title

def WriteEventPages(options, fm, events, calendars):
  for event in events:
    if event.calendar_title in ("Stanford Humanities Center Events",
                                "Co-sponsored Events Held at the Humanities Center",
                                "Test SHC Calendar"):
      tmpl = "shc_event.tmpl"
    else:
      tmpl = "workshop_event.tmpl"
    fm.save(options.output_dir + event.uri(),
            str(Template(file=tmpl,
                          searchList=[{"event": event,
                                       "calendar_title": event.calendar_title,
                                       "calendar_urls": [(c.calendar_name, c.landing_page_uri) for c in calendars],
                                       "forward_url": None,
                                       "forward_text": None,
                                       "back_url": None,
                                       "back_text": None}])))

def WritePostPages(options, fm, all_posts):
  for post in all_posts:
    tmpl = "post-template.tmpl"
    fm.save(options.output_dir + post.uri(),
            str(Template(file=tmpl,
                         searchList=[{"post" : post,
                                      "title": post.title,
                                      "published" : post.published,
                                      "content" : post.content,
                                      "categories" : post.categories}])))



def SanityCheck(fm, options):
  #pprint(sorted(fm.files.keys()))

  assert fm.HasFile(options.output_dir + "events/calendar/index.html")
  assert fm.HasFile(options.output_dir + "workshops/calendar/index.html")
  assert fm.HasFile(options.output_dir + "events/calendar/2012-02.html")
  assert fm.HasFile(options.output_dir + "events/calendar/2012-02.mini.html")
  assert fm.HasFile(options.output_dir + "workshops/calendar/2012-02.html")
  assert fm.HasFile(options.output_dir + "workshops/calendar/2012-02.mini.html")
  assert fm.HasFile(options.output_dir + "events/calendar/test-shc-calendar.html")
  assert fm.HasFile(options.output_dir + "workshops/calendar/test-workshop-calendar.html")
  assert fm.HasFile(options.output_dir + "events/calendar/2012-01-test-shc-calendar.html")
  assert fm.HasFile(options.output_dir + "events/calendar/2012-01-test-shc-calendar.mini.html")
  assert fm.HasFile(options.output_dir + "events/calendar/2012-03-test-shc-calendar.html")
  assert fm.HasFile(options.output_dir + "events/calendar/2012-03-test-shc-calendar.mini.html")
  assert fm.HasFile(options.output_dir + "events/calendar/2012-01-test-workshop-calendar.html")
  assert fm.HasFile(options.output_dir + "events/calendar/2012-01-test-workshop-calendar.mini.html")
  assert fm.HasFile(options.output_dir + "events/calendar/2012-03-test-workshop-calendar.html")
  assert fm.HasFile(options.output_dir + "events/calendar/2012-03-test-workshop-calendar.mini.html")
  assert fm.HasFile(options.output_dir + "events/calendar/2012-1-9-all-day-event.html")
  assert fm.HasFile(options.output_dir + "events/calendar/2012-1-9-all-day-workshop-event.html")
  assert fm.HasFile(options.output_dir + "events/calendar/2012-1-10-location-only-workshop-event.html")
  assert fm.HasFile(options.output_dir + "events/calendar/2012-1-10-location-only-event.html")
  assert fm.HasFile(options.output_dir + "events/calendar/2012-1-11-multi-day-workshop-event.html")
  assert fm.HasFile(options.output_dir + "events/calendar/2012-1-11-multi-day-event.html")
  #assert fm.HasFile(options.output_dir + "events/calendar/2012-1-14-event-to-be-changed.html")
  #assert fm.HasFile(options.output_dir + "events/calendar/2012-1-14-workshop-event-to-be-changed.html")
  assert fm.HasFile(options.output_dir + "events/calendar/2012-3-29-far-away-shc-event.html")
  assert fm.HasFile(options.output_dir + "events/calendar/2012-3-30-far-away-workshop-event.html")

  shc_test_text = fm.GetFile(options.output_dir + "events/calendar/test-shc-calendar.html")
  dom = etree.HTML(shc_test_text)
  MyAssert(dom.xpath('//title')[0].text,'Test SHC Calendar | Stanford Humanities Center')
  assert dom.xpath('//div[@id = "topnext"]')
  MyAssert(dom.xpath('//div[@id = "topnext"]/a')[0].get('href'), "../../events/calendar/2012-03-test-shc-calendar.html")
  MyAssert(dom.xpath('//div[@id = "topnext"]/a')[0].text, u"Mar 2012\xbb")
  assert dom.xpath('//div[@id = "topback"]')
  MyAssert(dom.xpath('//div[@id = "topback"]/a')[0].get('href'), "../../events/calendar/2012-01-test-shc-calendar.html")
  MyAssert(dom.xpath('//div[@id = "topback"]/a')[0].text, u"\xabJan 2012")
  assert dom.xpath('//div[@id = "bottomnext"]')
  MyAssert(dom.xpath('//div[@id = "bottomnext"]/a')[0].get('href'), "../../events/calendar/2012-03-test-shc-calendar.html")
  MyAssert(dom.xpath('//div[@id = "bottomnext"]/a')[0].text, u"Mar 2012\xbb")
  assert dom.xpath('//div[@id = "bottomback"]')
  MyAssert(dom.xpath('//div[@id = "bottomback"]/a')[0].get('href'), "../../events/calendar/2012-01-test-shc-calendar.html")
  MyAssert(dom.xpath('//div[@id = "bottomback"]/a')[0].text, u"\xabJan 2012")

  workshop_test_text = fm.GetFile(options.output_dir + "workshops/calendar/test-workshop-calendar.html")
  dom = etree.HTML(workshop_test_text)
  MyAssert(dom.xpath('//title')[0].text, 'Test Workshop Calendar | Stanford Humanities Center')
  assert dom.xpath('//div[@id = "topnext"]')
  MyAssert(dom.xpath('//div[@id = "topnext"]/a')[0].get('href'), "../../events/calendar/2012-03-test-workshop-calendar.html")
  MyAssert(dom.xpath('//div[@id = "topnext"]/a')[0].text, u"Mar 2012\xbb")
  assert dom.xpath('//div[@id = "topback"]')
  MyAssert(dom.xpath('//div[@id = "topback"]/a')[0].get('href'), "../../events/calendar/2012-01-test-workshop-calendar.html")
  MyAssert(dom.xpath('//div[@id = "topback"]/a')[0].text, u"\xabJan 2012")
  assert dom.xpath('//div[@id = "bottomnext"]')
  MyAssert(dom.xpath('//div[@id = "bottomnext"]/a')[0].get('href'), "../../events/calendar/2012-03-test-workshop-calendar.html")
  MyAssert(dom.xpath('//div[@id = "bottomnext"]/a')[0].text, u"Mar 2012\xbb")
  assert dom.xpath('//div[@id = "bottomback"]')
  MyAssert(dom.xpath('//div[@id = "bottomback"]/a')[0].get('href'), "../../events/calendar/2012-01-test-workshop-calendar.html")
  MyAssert(dom.xpath('//div[@id = "bottomback"]/a')[0].text, u"\xabJan 2012")

  jan_shc_text = fm.GetFile(options.output_dir + "events/calendar/2012-01-test-shc-calendar.html")
  dom = etree.HTML(jan_shc_text)
  MyAssert(dom.xpath('//title')[0].text,'Test SHC Calendar: January 2012 | Stanford Humanities Center')
  assert dom.xpath('//iframe[@id = "minical"]')
  MyAssert(dom.xpath('//iframe[@id = "minical"]')[0].get('src'), "../../events/calendar/2012-01-test-shc-calendar.mini.html")
  assert dom.xpath('//div[@id = "topnext"]')
  MyAssert(dom.xpath('//div[@id = "topnext"]/a')[0].get('href'), "../../events/calendar/2012-03-test-shc-calendar.html")
  MyAssert(dom.xpath('//div[@id = "topnext"]/a')[0].text, u"Mar 2012\xbb")
  assert not dom.xpath('//div[@id = "topback"]'), "Expected None, found %r" % dom.xpath('//div[@id = "topback"]')
  MyAssert(dom.xpath('//div[@id = "bottomnext"]/a')[0].get('href'), "../../events/calendar/2012-03-test-shc-calendar.html")
  MyAssert(dom.xpath('//div[@id = "bottomnext"]/a')[0].text, u"Mar 2012\xbb")
  assert not dom.xpath('//div[@id = "bottomback"]')


  mar_shc_text = fm.GetFile(options.output_dir + "events/calendar/2012-03-test-shc-calendar.html")
  dom = etree.HTML(mar_shc_text)
  MyAssert(dom.xpath('//title')[0].text,'Test SHC Calendar: March 2012 | Stanford Humanities Center')
  assert dom.xpath('//iframe[@id = "minical"]')
  MyAssert(dom.xpath('//iframe[@id = "minical"]')[0].get('src'), "../../events/calendar/2012-03-test-shc-calendar.mini.html")
  assert not dom.xpath('//div[@id = "topnext"]')
  assert dom.xpath('//div[@id = "topback"]')
  MyAssert(dom.xpath('//div[@id = "topback"]/a')[0].get('href'), "../../events/calendar/2012-01-test-shc-calendar.html")
  MyAssert(dom.xpath('//div[@id = "topback"]/a')[0].text, u"\xabJan 2012")
  assert not dom.xpath('//div[@id = "bottomnext"]')
  assert dom.xpath('//div[@id = "bottomback"]')
  MyAssert(dom.xpath('//div[@id = "bottomback"]/a')[0].get('href'), "../../events/calendar/2012-01-test-shc-calendar.html")
  MyAssert(dom.xpath('//div[@id = "bottomback"]/a')[0].text, u"\xabJan 2012")

  jan_workshop_text = fm.GetFile(options.output_dir + "events/calendar/2012-01-test-workshop-calendar.html")
  dom = etree.HTML(jan_workshop_text)
  MyAssert(dom.xpath('//title')[0].text,'Test Workshop Calendar: January 2012 | Stanford Humanities Center')
  assert dom.xpath('//iframe[@id = "minical"]')
  MyAssert(dom.xpath('//iframe[@id = "minical"]')[0].get('src'), "../../events/calendar/2012-01-test-workshop-calendar.mini.html")
  assert dom.xpath('//div[@id = "topnext"]')
  MyAssert(dom.xpath('//div[@id = "topnext"]/a')[0].get('href'), "../../events/calendar/2012-03-test-workshop-calendar.html")
  MyAssert(dom.xpath('//div[@id = "topnext"]/a')[0].text, u"Mar 2012\xbb")
  assert not dom.xpath('//div[@id = "topback"]')
  MyAssert(dom.xpath('//div[@id = "bottomnext"]/a')[0].get('href'), "../../events/calendar/2012-03-test-workshop-calendar.html")
  MyAssert(dom.xpath('//div[@id = "bottomnext"]/a')[0].text, u"Mar 2012\xbb")
  assert not dom.xpath('//div[@id = "bottomback"]')

  mar_workshop_text = fm.GetFile(options.output_dir + "events/calendar/2012-03-test-workshop-calendar.html")
  dom = etree.HTML(mar_workshop_text)
  MyAssert(dom.xpath('//title')[0].text,'Test Workshop Calendar: March 2012 | Stanford Humanities Center')
  assert dom.xpath('//iframe[@id = "minical"]')
  MyAssert(dom.xpath('//iframe[@id = "minical"]')[0].get('src'), "../../events/calendar/2012-03-test-workshop-calendar.mini.html")
  assert not dom.xpath('//div[@id = "topnext"]')
  assert dom.xpath('//div[@id = "topback"]')
  MyAssert(dom.xpath('//div[@id = "topback"]/a')[0].get('href'), "../../events/calendar/2012-01-test-workshop-calendar.html")
  MyAssert(dom.xpath('//div[@id = "topback"]/a')[0].text, u"\xabJan 2012")
  assert not dom.xpath('//div[@id = "bottomnext"]')
  assert dom.xpath('//div[@id = "bottomback"]')
  MyAssert(dom.xpath('//div[@id = "bottomback"]/a')[0].get('href'), "../../events/calendar/2012-01-test-workshop-calendar.html")
  MyAssert(dom.xpath('//div[@id = "bottomback"]/a')[0].text, u"\xabJan 2012")

  feb_landing_page = fm.GetFile(options.output_dir + "events/calendar/2012-02.html")
  dom = etree.HTML(feb_landing_page)
  MyAssert(dom.xpath('//title')[0].text,'Events Calendar: February 2012 | Stanford Humanities Center')
  assert dom.xpath('//iframe[@id = "minical"]')
  MyAssert(dom.xpath('//iframe[@id = "minical"]')[0].get('src'), "../../events/calendar/2012-02.mini.html")
  assert dom.xpath('//div[@id = "topnext"]')
  MyAssert(dom.xpath('//div[@id = "topnext"]/a')[0].get('href'), "../../events/calendar/2012-03.html")
  MyAssert(dom.xpath('//div[@id = "topnext"]/a')[0].text, u"Mar 2012\xbb")
  assert dom.xpath('//div[@id = "topback"]')
  MyAssert(dom.xpath('//div[@id = "topback"]/a')[0].get('href'), "../../events/calendar/2012-01.html")
  MyAssert(dom.xpath('//div[@id = "topback"]/a')[0].text, u"\xabJan 2012")
  assert dom.xpath('//div[@id = "bottomnext"]')
  MyAssert(dom.xpath('//div[@id = "bottomnext"]/a')[0].get('href'), "../../events/calendar/2012-03.html")
  MyAssert(dom.xpath('//div[@id = "bottomnext"]/a')[0].text, u"Mar 2012\xbb")
  assert dom.xpath('//div[@id = "bottomback"]')
  MyAssert(dom.xpath('//div[@id = "bottomback"]/a')[0].get('href'), "../../events/calendar/2012-01.html")
  MyAssert(dom.xpath('//div[@id = "bottomback"]/a')[0].text, u"\xabJan 2012")

  feb_workshop_page = fm.GetFile(options.output_dir + "workshops/calendar/2012-02.html")
  dom = etree.HTML(feb_workshop_page)
  MyAssert(dom.xpath('//title')[0].text,'Workshop Calendar: February 2012 | Stanford Humanities Center')
  assert dom.xpath('//iframe[@id = "minical"]')
  MyAssert(dom.xpath('//iframe[@id = "minical"]')[0].get('src'), "../../workshops/calendar/2012-02.mini.html")
  assert dom.xpath('//div[@id = "topnext"]')
  MyAssert(dom.xpath('//div[@id = "topnext"]/a')[0].get('href'), "../../workshops/calendar/2012-03.html")
  MyAssert(dom.xpath('//div[@id = "topnext"]/a')[0].text, u"Mar 2012\xbb")
  assert dom.xpath('//div[@id = "topback"]')
  MyAssert(dom.xpath('//div[@id = "topback"]/a')[0].get('href'), "../../workshops/calendar/2012-01.html")
  MyAssert(dom.xpath('//div[@id = "topback"]/a')[0].text, u"\xabJan 2012")
  assert dom.xpath('//div[@id = "bottomnext"]')
  MyAssert(dom.xpath('//div[@id = "bottomnext"]/a')[0].get('href'), "../../workshops/calendar/2012-03.html")
  MyAssert(dom.xpath('//div[@id = "bottomnext"]/a')[0].text, u"Mar 2012\xbb")
  assert dom.xpath('//div[@id = "bottomback"]')
  MyAssert(dom.xpath('//div[@id = "bottomback"]/a')[0].get('href'), "../../workshops/calendar/2012-01.html")
  MyAssert(dom.xpath('//div[@id = "bottomback"]/a')[0].text, u"\xabJan 2012")

  # TODO(chris): Add assertions for the <iframe> src. (Add an id to the iframe). Add assertions for the existence of the minicals
if __name__ == "__main__":
  main(sys.argv)
