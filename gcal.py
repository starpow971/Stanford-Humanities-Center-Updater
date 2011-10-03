# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: interface with calendar server, parse calendar responses, 
# produce useful event objects.

import datetime
import re
import xml.etree.ElementTree as ET


class Event:
	"""Represents a Google Calendar event."""
	
	def __init__(self, calendar_title="", event_title="", event_id="",
	             start_time=None, end_time=None, location="", status="", 
	             description=""):
		self.calendar_title = calendar_title
		self.event_title = event_title
		self.event_id = event_id
		self.start_time = start_time  # A datetime.
		self.end_time = end_time  # A datetime.
		self.location = location
		self.status = status  # like "confirmed" or something.
		self.description = description
		
	def __repr__(self):
		return "<calendar: '%s' id: '%s' title: '%s' description: %r>" % (
				self.calendar_title, self.event_id, self.event_title, 
				self.description[:40])
				

class EventDescription:
	"""Represents data embedded in a Google Calendar description."""
	
	def __init__(self, start_time=None, end_time=None, location=""):
		self.start_time = start_time #A datetime.
		self.end_time = end_time #A datetime.
		self.location = location
		
	def __repr__(self):
		return "<start time: %r end time: %r location: %s>" % (
		    self.start_time, self.end_time, self.location)
		
	def __eq__(self, other):
		return (self.start_time == other.start_time and 
						self.end_time == other.end_time and
						self.location == other.location)
		

NAMESPACE = "{http://www.w3.org/2005/Atom}"
ENTRY_TAG = NAMESPACE + "entry"
TITLE_TAG = NAMESPACE + "title"
CONTENT_TAG = NAMESPACE + "content"
ID_TAG = NAMESPACE + "id"

DESCRIPTION_WHERE_RE = re.compile(r'''Where:(?P<location>(\s+\w+)+)''')
assert DESCRIPTION_WHERE_RE
DESCRIPTION_WHEN_RE = re.compile(
    r'''When:\s*(?P<weekday>\w+)\s+(?P<month>\w+)\s+(?P<day>\d+),\s+'''
    r'''(?P<year>\d+)\s+'''
    r'''(?P<start_hour>\d+):(?P<start_min>\d+)(?P<start_thing>am|pm)\s+to\s+'''
    r'''(?P<end_hour>\d+):(?P<end_min>\d+)(?P<end_thing>am|pm)\s+'''
    r'''(?P<timezone>\w+)''')
assert DESCRIPTION_WHEN_RE
MONTHS = {
		"jan": 1,
		"feb": 2,
		"mar": 3,
		"apr": 4,
		"may": 5,
		"jun": 6,
		"jul": 7,
		"aug": 8,
		"sep": 9,
		"oct": 10,
		"nov": 11,
		"dec": 12 }

class ParseError(Exception): pass

def parse_description(description):
	"""Parses a Google Calendar description.
	
	Args: 
		description: a string representing the content tag from a Google calendar feed.
		
	Returns: An event description object."""
	when = DESCRIPTION_WHEN_RE.search(description)
	if not when:
		raise ParseError()
	when = when.groupdict()
	start_hour = int(when["start_hour"])
	if when["start_thing"] == "pm":
		start_hour += 12
	start_time = datetime.datetime(
	    int(when["year"]),
	    MONTHS[when["month"].lower()],
	    int(when["day"]),
	    start_hour,
	    int(when["start_min"]))
	end_hour = int(when["end_hour"])
	if when["end_thing"] == "pm":
		end_hour += 12
	end_time = datetime.datetime(
	    int(when["year"]),
	    MONTHS[when["month"].lower()],
	    int(when["day"]),
	    end_hour,
	    int(when["end_min"]))
	where = DESCRIPTION_WHERE_RE.search(description)
	if not where:
		raise ParseError()
	where = where.groupdict()
	location = where["location"].strip()
	return EventDescription(start_time=start_time, end_time=end_time, 
													location=location)
	    

def make_event(entry, cal_title):
  titletag = entry.find(TITLE_TAG)
  if titletag is None:
    #todo: log an error
    return

  contenttag = entry.find(CONTENT_TAG)
  if contenttag is None:
    #todo: log an error
    return
    
  idtag = entry.find(ID_TAG)
  if idtag is None:
  	#todo: log an error
  	return
  	
  id = entry.find(ID_TAG)
  (url, id_key) = id.text.rsplit("/", 1)
  
  return Event(calendar_title=cal_title, event_id=id_key, event_title=titletag.text, description=contenttag.text)

def parse_feed(xml):
	feed = ET.parse(xml)
	cal_title = feed.find(TITLE_TAG)
	entries = feed.findall(ENTRY_TAG)
	return [make_event(entry, cal_title.text) for entry in entries]
		
  	
parse_feed("calendar.xml")