#!/usr/bin/env python
# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE.
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: Pulls events from database and writes them to disc.


from Cheetah.Template import Template
from optparse import OptionParser
import datetime
import re
import sys

import datastore
import config
import file_manager

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

  calendar_urls = [(name, uri(name)) for name in config.calendar_ids.keys()]
  fm.save(options.output_dir + "events/calendar/index.html",
          str(Template(file="calendar-landing-page.tmpl",
                       searchList=[{"events": events,
                                    "calendar_title": "Events Calendar"}])))

  fm.save(options.output_dir + "workshops/calendar/index.html",
          str(Template(file="workshop-landing-page.tmpl",
                       searchList=[{"events": events,
                                    "calendar_title": "Workshop Calendar",
                                    "calendar_urls": calendar_urls}])))

  for event in all_events:
    if event.IsWorkshop():
      tmpl = "workshop_event.tmpl"
    else:
      tmpl = "shc_event.tmpl"
    fm.save(options.output_dir + event.uri(),
            str(Template(file=tmpl,
                         searchList=[{"event": event,
                                      "calendar_title": event.calendar_title,
                                      "calendar_urls": calendar_urls}])))

  events_by_calendar = {}
  for cal_id in config.calendar_ids.iterkeys():
    events_by_calendar[cal_id] = []
  for e in events:
    events_by_calendar[e.calendar_title].append(e)
  for calendar_name, calendar_events in events_by_calendar.iteritems():
    if event.IsWorkshop():
      tmpl = "workshop-landing-page.tmpl"
    else:
      tmpl= "calendar-landing-page.tmpl"
    fm.save(options.output_dir + uri(calendar_name),
            str(Template(file=tmpl,
                         searchList=[{"events": calendar_events,
                                      "calendar_title": calendar_name,
                                      "calendar_urls": calendar_urls}])))

  cal_months = {}
  all_workshop_months = {}
  all_event_months = {}
  for event in all_events:
    cal_months.setdefault(event.calendar_title, {}).setdefault(event.yearmonth(), []).append(e)
  if event.IsWorkshop():
    all_workshop_months.setdefault(event.yearmonth(), []).append(e)
  else:
    all_event_months.setdefault(event.yearmonth(), []).append(e)


  #print fm.show_diff()
  fm.commit()

def uri(calendar_title):
  if IsWorkshop(calendar_title):
    return "workshops/calendar/%s.html" % (friendly_title(calendar_title))
  else:
    return "events/calendar/%s.html" % (friendly_title(calendar_title))

def friendly_title(calendar_title):
  title = re.sub(" +", "-", calendar_title.lower())
  title = re.sub("[^-a-z0-9]", "", title)
  return title

def IsWorkshop(calendar_title):
  return calendar_title not in ("Stanford Humanities Center Events", "Co-sponsored Events Held at the Humanities Center")


if __name__ == "__main__":
  main(sys.argv)
