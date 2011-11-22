#!/usr/bin/env python
# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE.
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: Pulls events from database and writes them to disc.


from Cheetah.Template import Template
from optparse import OptionParser
import bisect
import datetime
import re
import sys

import datastore
import config
import file_manager


class PostFlipBook(self):
  """Sets up the flipbooks for posts- yearmonths, tags, all posts."""
  def __init__(self, uri, pretty_name):
    self.uri = uri
    self.pretty_name = pretty_name
    self.posts = []

  def render(self, fm):
    pages = group(self.posts, 10)
    for pg_num, posts in enumerate(pages):
      tpl = self.page_uri(pg_num)
    fm.save(tpl, searchList=[{"posts": posts}])

  def page_uri(self, pg_num):
    if pg_num == 0:
      return "news-videos/news/index.html"
    else:
      return "news-videos/news/index" + pg_num + ".html"

class FlipbookIndex(self):
  def __init__(self, yearmonth, categories):
    self.yearmonth = yearmonth
    self.categories = categories

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
  options, args = op.parse_args(argv[1:])
  if not options.output_dir.endswith("/"):
    options.output_dir += "/"
  return options, args


def main(argv):
  options, args = parse_args(argv)
  fm = file_manager.FileManager()
  ds = datastore.DataStore("database.db")

  start_date = datetime.datetime.now()
  end_date = start_date + datetime.timedelta(31)

  # NOTE(scottrw): the list() function is necessary because GetEventsInRange
  # returns a generator, which is exhausted by the first template, leaving no
  # events left for the second template!
  events = list(ds.GetEventsInRange(start_date, end_date))
  all_events = list(ds.GetAllEvents())
  all_posts =  list(ds.GetAllPosts())


  cal_months = {}
  all_workshop_months = {}
  all_event_months = {}
  for event in all_events:
    cal_months.setdefault(event.calendar_title, {}).setdefault(event.yearmonth(), []).append(event)
    all_event_months.setdefault(event.yearmonth(), []).append(event)

  all_posts_fb = PostFlipBook("news-videos/news/index.html", "All Posts")
  for post in all_posts:
    all_posts_fb.posts.append(post)


  calendar_urls = [(name, uri(name)) for name in config.calendar_ids.keys()]
  WriteUpcomingEvents(options, fm, events)
  WriteUpcomingWorkshops(options, fm, events, calendar_urls)
  WriteEventPages(options, fm, all_events, calendar_urls)
  WriteIndividualCalendars(options, fm, events, cal_months, calendar_urls, start_date, end_date)
  WritePerMonthCalendars(options, fm, all_event_months, calendar_urls)
  WritePerMonthWorkshopCalendars(options, fm, all_event_months, calendar_urls)
  WritePerCalPerMonthCalendars(options, fm, cal_months, calendar_urls)
  WritePostPages(options, fm, all_posts)

  #print fm.show_diff()
  fm.commit()


def WriteUpcomingEvents(options, fm, events):
  fm.save(options.output_dir + "events/calendar/index.html",
          str(Template(file="calendar-landing-page.tmpl",
                       searchList=[{"events": events,
                                    "calendar_title": "Events Calendar",
                                    "forward_url": events[-1].start_time.strftime('%Y-%m.html'),
                                    "forward_text": "All events for %s&raquo" % events[-1].start_time.strftime('%b %Y'),
                                    "back_url": events[0].start_time.strftime('%Y-%m.html'),
                                    "back_text": "All events for %s" % events[0].start_time.strftime('%b %Y')}])))

def WriteUpcomingWorkshops(options, fm, events, calendar_urls):
  fm.save(options.output_dir + "workshops/calendar/index.html",
          str(Template(file="workshop-landing-page.tmpl",
                       searchList=[{"events": events,
                                    "calendar_title": "Workshop Calendar",
                                    "calendar_urls": calendar_urls,
                                    "forward_url": events[-1].start_time.strftime('%Y-%m.html'),
                                    "forward_text": "All events for %s&raquo" % events[-1].start_time.strftime('%b %Y'),
                                    "back_url": events[0].start_time.strftime('%Y-%m.html'),
                                    "back_text": "All events for %s" % events[0].start_time.strftime('%b %Y')}])))

def WriteEventPages(options, fm, all_events, calendar_urls):
  for event in all_events:
    if event.calendar_title in ("Stanford Humanities Center Events", "Co-sponsored Events Held at the Humanities Center"):
      tmpl = "shc_event.tmpl"
    else:
      tmpl = "workshop_event.tmpl"
    fm.save(options.output_dir + event.uri(),
            str(Template(file=tmpl,
                         searchList=[{"event": event,
                                      "calendar_title": event.calendar_title,
                                      "calendar_urls": calendar_urls,
                                      "forward_url": None,
                                      "forward_text": None,
                                      "back_url": None,
                                      "back_text": None}])))

def WriteIndividualCalendars(options, fm, events, cal_months, calendar_urls, start_date, end_date):
  events_by_calendar = {}
  for cal_id in config.calendar_ids.iterkeys():
    events_by_calendar[cal_id] = []
  for e in events:
    events_by_calendar[e.calendar_title].append(e)
  for calendar_name, calendar_events in events_by_calendar.iteritems():
    if calendar_name in ("Stanford Humanities Center Events", "Co-sponsored Events Held at the Humanities Center"):
      tmpl = "calendar-landing-page.tmpl"
    else:
      tmpl = "workshop-landing-page.tmpl"
    if not calendar_events:
      all_events = cal_months.get(calendar_name, None)
      if not all_events:
        forward_url = None
        forward_text = None
        back_url = None
        back_text = None
      else:
        months = all_events.keys()
        months.sort()
        back_index = max(0, min(bisect.bisect_left(months, start_date), len(months) - 1) - 1)
        next_index = min(bisect.bisect_left(months, start_date), len(months) - 1)
        back_date = months[back_index]
        next_date = months[next_index]
        forward_url = "../../" + month_uri(next_date, calendar_name)
        forward_text = next_date.strftime('%b %Y') + "&raquo;"
        back_url = "../../" + month_uri(back_date, calendar_name)
        back_text = back_date.strftime('%b %Y')
    else:
      forward_url = "../../" + month_uri(calendar_events[-1].start_time, calendar_name)
      forward_text = calendar_events[-1].start_time.strftime('%b %Y') + "&raquo;"
      back_url = "../../" + month_uri(calendar_events[0].start_time, calendar_name)
      back_text = calendar_events[0].start_time.strftime('%b %Y')
    fm.save(options.output_dir + uri(calendar_name),
            str(Template(file=tmpl,
                         searchList=[{"events": calendar_events,
                                      "calendar_title": calendar_name,
                                      "calendar_urls": calendar_urls,
                                      "back_url": back_url,
                                      "back_text": back_text,
                                      "forward_url": forward_url,
                                      "forward_text": forward_text}])))


def WritePerMonthCalendars(options, fm, all_event_months, calendar_urls):
  month_events = sorted(all_event_months.items())
  months = [month for month, events in month_events]
  for (yearmonth, events), back, forward in zip(month_events,
                                                [None] + months[:-1],
                                                months[1:] + [None]):
    calendar_title = yearmonth.strftime("Events Calendar for %B %Y")
    #Render a calendar template into the right file
    fm.save(options.output_dir + yearmonth.strftime("events/calendar/%Y-%m.html"),
            str(Template(file="calendar-landing-page.tmpl",
                         searchList=[{"events": events,
                                      "calendar_title": calendar_title,
                                      "back_url": back and back.strftime('%Y-%m.html'),
                                      "back_text": back and back.strftime ('%b %Y'),
                                      "forward_url": forward and forward.strftime('%Y-%m.html'),
                                      "forward_text": forward and forward.strftime('%b %Y') + "&raquo;",
                                      "calendar": calendar_title}])))

def WritePerMonthWorkshopCalendars(options, fm, all_event_months, calendar_urls):
  month_events = sorted(all_event_months.items())
  months = [month for month, events in month_events]
  for (yearmonth, events), back, forward in zip(month_events,
                                                [None] + months[:-1],
                                                months[1:] + [None]):
    calendar_title = yearmonth.strftime("Workshop Calendar for %B %Y")
    #Render a calendar template into the right file
    fm.save(options.output_dir + yearmonth.strftime("workshops/calendar/%Y-%m.html"),
            str(Template(file="workshop-landing-page.tmpl",
                         searchList=[{"events": events,
                                      "calendar_title": calendar_title,
                                      "calendar_urls": calendar_urls,
                                      "back_url": back and back.strftime('%Y-%m.html'),
                                      "back_text": back and back.strftime ('%b %Y'),
                                      "forward_url": forward and forward.strftime('%Y-%m.html'),
                                      "forward_text": forward and forward.strftime('%b %Y') + "&raquo;",
                                      "calendar": calendar_title}])))

def WritePerCalPerMonthCalendars(options, fm, cal_months, calendar_urls):
  for calendar, all_event_months in cal_months.iteritems():
    month_events = sorted(all_event_months.items())
    months = [month for month, events in month_events]
    for (yearmonth, events), back, forward in zip(month_events,
                                                  [None] + months[:-1],
                                                  months[1:] + [None]):
      calendar_title = calendar + " Events For " + yearmonth.strftime("%B %Y")
      #Render a calendar template into the right file
      if calendar in ("Stanford Humanities Center Events", "Co-sponsored Events Held at the Humanities Center"):
        tmpl = "calendar-landing-page.tmpl"
      else:
        tmpl = "workshop-landing-page.tmpl"
      fm.save(options.output_dir + month_uri(yearmonth, calendar),
              str(Template(file=tmpl,
                           searchList=[{"events": events,
                                        "calendar_title": calendar_title,
                                        "calendar_urls": calendar_urls,
                                        "back_url": back and "../../" + month_uri(back, calendar),
                                        "back_text": back and back.strftime('%b %Y'),
                                        "forward_url": forward and "../../" + month_uri(forward, calendar),
                                        "forward_text": forward and forward.strftime('%b %Y') + "&raquo;",
                                        "calendar": calendar}])))

def month_uri(yearmonth, calendar):
  return yearmonth.strftime("events/calendar/%%Y-%%m-%s.html" % friendly_title(calendar))

def uri(calendar_title):
  if calendar_title == "Stanford Humanities Center Events":
    return "events/calendar/%s.html" % (friendly_title(calendar_title))
  elif calendar_title == "Co-sponsored Events Held at the Humanities Center":
    return "events/calendar/%s.html" % (friendly_title(calendar_title))
  else:
    return "workshops/calendar/%s.html" % (friendly_title(calendar_title))


def friendly_title(calendar_title):
  title = re.sub(" +", "-", calendar_title.lower())
  title = re.sub("[^-a-z0-9]", "", title)
  return title


def WritePostPages(options, fm, all_posts):
  for post in all_posts:
    tmpl = "news-template.tmpl"
    fm.save(options.output_dir + post.uri(),
            str(Template(file=tmpl,
                         searchList=[{"post": post,
                                      "title": post.title}])))

if __name__ == "__main__":
  main(sys.argv)
