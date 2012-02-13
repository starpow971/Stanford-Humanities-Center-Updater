# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE.
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: interface with calendar server, parse calendar responses,
# produce useful event objects.

import collections
import datetime
import re
import logging
import xml.etree.ElementTree as ET


#Event = collections.namedtuple('Event', 'calendar_title, event_title, event_id, start_time, end_time, location, status, description, updated, is_all_day, thumbnail, full_image'


class Event:
  """Represents a Google Calendar event."""

  def __init__(self, calendar_title="", event_title="", event_id="",
               start_time=None, end_time=None, location="", status="",
               description="", updated="", is_all_day=False, thumbnail="", full_image="", endowment_title=""):
    self.calendar_title = calendar_title
    self.event_title = event_title
    self.event_id = event_id
    self.start_time = start_time  # A datetime.
    self.end_time = end_time  # A datetime.
    self.location = location
    self.status = status  # like "confirmed" or something.
    self.description = description
    self.updated = updated
    self.is_all_day = is_all_day  # for events that have no real times
    self.thumbnail = thumbnail #for events that have Picasa images attached
    self.full_image = full_image #for events that have Picasa images attached
    self.endowment_title = endowment_title #for events that are endowed

  def uri(self):
    return "events/calendar/%s-%s-%s-%s.html" % (self.start_time.year,
            self.start_time.month, self.start_time.day, self.friendly_title())

  def friendly_title(self):
    title = re.sub(" +", "-", self.event_title.lower())
    title = re.sub("[^-a-z0-9]", "", title)
    return title

  def yearmonth(self):
    return datetime.datetime(self.start_time.year, self.start_time.month, 1)

  #def IsWorkshop(self):
    #return self.calendar_title not in ("Stanford Humanities Center Events", "Co-sponsored Events Held at the Humanities Center")

  def __repr__(self):
    return ("\n<calendar_title: %(calendar_title)r\n "
            "event_title: %(event_title)r\n "
            "event_id: %(event_id)r\n "
            "start_time: %(start_time)r\n "
            "is_all_day: %(is_all_day)r\n "
            "end_time: %(end_time)r\n "
            "location: %(location)r\n "
            "status: %(status)r\n "
            "description: %(description)r\n"
            "thumbnail: %(thumbnail)r\n"
            "full_image: %(full_image)r\n"
            "endowment_title: %(endowment_title)r\n"
            "updated: %(updated)r"
            ">") % {
              'calendar_title': self.calendar_title,
              'event_title': self.event_title,
              'event_id': self.event_id,
              'start_time': self.start_time,
              'is_all_day': self.is_all_day,
              'end_time': self.end_time,
              'location': self.location,
              'status': self.status,
              'description': self.description[:40],
              'thumbnail': self.thumbnail,
              'full_image': self.full_image,
              'endowment_title': self.endowment_title,
              'updated': self.updated}

  def __eq__(self, other):
    return (
      self.calendar_title == other.calendar_title and
      self.event_title == other.event_title and
      self.event_id == other.event_id and
      self.start_time == other.start_time and
      self.end_time == other.end_time and
      self.location == other.location and
      self.status == other.status and
      self.description == other.description and
      self.updated == other.updated and
      self.is_all_day == other.is_all_day and
      self.thumbnail == other.thumbnail and
      self.full_image == other.full_image and
      self.endowment_title == other.endowment_title)


class EventDescription:
  """Represents data embedded in a Google Calendar description."""

  def __init__(self, start_time=None, end_time=None, location="", status="",
               description="", is_all_day=False, thumbnail="", full_image="", endowment_title=""):
    self.start_time = start_time #A datetime.
    self.is_all_day = is_all_day
    self.end_time = end_time #A datetime.
    self.location = location
    self.status = status
    self.description = description
    self.thumbnail = thumbnail
    self.full_image = full_image
    self.endowment_title = endowment_title

  def __repr__(self):
    return ("<start time: %r end time: %r location: %s status: %s "
            "description: %s is_all_day: %r thumbnail: %r "
            "full image: %r endowment_title: %r>") % (
        self.start_time, self.end_time, self.location, self.status,
        self.description, self.is_all_day, self.thumbnail, self.full_image, self.endowment_title)

  def __eq__(self, other):
    return (self.start_time == other.start_time and
            self.end_time == other.end_time and
            self.location == other.location and
            self.status == other.status and
            self.description == other.description and
            self.is_all_day == other.is_all_day and
            self.thumbnail == other.thumbnail and
            self.full_image == other.full_image and
            self.endowment_title == other.endowment_title)


NAMESPACE = "{http://www.w3.org/2005/Atom}"
ENTRY_TAG = NAMESPACE + "entry"
TITLE_TAG = NAMESPACE + "title"
CONTENT_TAG = NAMESPACE + "content"
ID_TAG = NAMESPACE + "id"
UPDATED_TAG = NAMESPACE + "updated"

DESCRIPTION_STATUS_RE = re.compile(r'''Event Status:(?P<status>(\s+\w+)+)''')
assert DESCRIPTION_STATUS_RE
DESCRIPTION_WHERE_RE = re.compile(r'''Where:(?P<location>(\s+\w+)+)''')
assert DESCRIPTION_WHERE_RE
DESCRIPTION_WHEN_RE = re.compile(r'''When: (?P<when>[^<]+)''')
assert DESCRIPTION_WHEN_RE

class ParseError(Exception): pass

def parse_dates(when):
  """Parses a Google Calendar when annotation."""
  is_all_day = " to " not in when
  if is_all_day:
    start_string = when
    end_string = when
  else:
    start_string, end_string = when.split(" to ", 1)

  start_format = "%a %b %d, %Y"
  if not is_all_day:
    start_format += " %I"
  if ':' in start_string:
    start_format += ":%M"
  if not is_all_day:
    start_format += "%p"

  if is_all_day:
    end_format = start_format
  else:
    end_format = ""
    if ',' in end_string:
      end_format += "%a %b %d, %Y "
    end_format += "%I"
    if ':' in end_string:
      end_format += ":%M"
    end_format += "%p %Z"

  start = datetime.datetime.strptime(start_string.encode('ascii', 'ignore'),
                                     start_format)
  end = datetime.datetime.strptime(end_string.encode('ascii', 'ignore'),
                                   end_format)
  end = datetime.datetime(start.year, start.month, start.day, end.hour,
                          end.minute)
  return start, end, is_all_day

def parse_description(description):
  """Parses a Google Calendar description.

  Args:
    description: a string representing the content tag from a Google calendar
    feed.

  Returns: An event description object."""
  if "Event Description: " in description:
    meta, description = description.split("Event Description: ", 1)
  else:
    meta = description
    description = None
  #import pdb; pdb.set_trace()
  if description and "thumbnail: " in description:
    description, image = (p.strip() for p in description.split("thumbnail: ", 1))
    thumbnail, full_image = (p.strip() for p in image.split("full_image: ", 1))
  else:
    description = description
    thumbnail = None
    full_image = None
  if description and "endowment_title: " in description:
    description, endowment_title = (p.strip() for p in description.split("endowment_title: ", 1))
  else:
    description =  description
    endowment_title = None
  if description and "thumbnail: " in description and not "full_image: " in description:
    print "error for description in event: ", event.event_title, ":thumbnail but no full_image"
  if description and "full_image: " in description and not "thumbnail: " in description:
    print "error for description in event: ", event.event_title, ":full_image but no thumbnail"
  if (description and 'full_image: ' and 'thumbnail: ' in description and description.find('full_image: ') < description.find('thumbnail: ')):
    print "Error in description for event: ", event.event_title, ":thumbnail must come before full_image"
  when = DESCRIPTION_WHEN_RE.search(meta)
  if not when:
    logging.warning("No when: block found in %s" % meta)
    return
  when = when.groupdict()
  when = when["when"].strip()
  start_time, end_time, is_all_day = parse_dates(when)
  where = DESCRIPTION_WHERE_RE.search(meta)
  if where:
    where = where.groupdict()
    location = where["location"].strip()
  else:
    location = None
  status = DESCRIPTION_STATUS_RE.search(meta)
  if not status:
    logging.warning("No when: block found in %s" % meta)
    return
  status = status.groupdict()
  event_status = status["status"].strip()
  return EventDescription(start_time=start_time, end_time=end_time,
                          is_all_day=is_all_day,
                          location=location, status=event_status,
                          description=description, thumbnail=thumbnail, full_image=full_image, endowment_title=endowment_title)


def make_event(entry, cal_title):
  titletag = entry.find(TITLE_TAG)
  if titletag is None:
    logging.warning("No title tag found in %s" % entry)
    return

  contenttag = entry.find(CONTENT_TAG)
  if contenttag is None:
    logging.warning("No content tag found in %s" % entry)
    return

  idtag = entry.find(ID_TAG)
  if idtag is None:
    logging.warning("No id tag found in %s" % entry)
    return

  id = entry.find(ID_TAG)
  (url, id_key) = id.text.rsplit("/", 1)

  updatedtag = entry.find(UPDATED_TAG)
  if updatedtag is None:
    logging.warning("No updated tag found in %s" % entry)
    return

  event_description = parse_description(contenttag.text)

  return Event(calendar_title=cal_title, event_id=id_key,
               updated=updatedtag.text,
               event_title=titletag.text,
               start_time=event_description.start_time,
               is_all_day=event_description.is_all_day,
               end_time=event_description.end_time,
               location=event_description.location,
               status=event_description.status,
               description=event_description.description,
               thumbnail=event_description.thumbnail,
               full_image=event_description.full_image,
               endowment_title=event_description.endowment_title)

def parse_feed(xml):
  feed = ET.parse(xml)
  cal_title = feed.find(TITLE_TAG)
  entries = feed.findall(ENTRY_TAG)
  return [make_event(entry, cal_title.text) for entry in entries]

