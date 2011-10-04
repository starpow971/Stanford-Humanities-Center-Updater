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
		return ("\n<calendar_title: %(calendar_title)r\n "
		        "event_title: %(event_title)r\n "
		        "event_id: %(event_id)r\n "
		        "start_time: %(start_time)r\n "
		        "end_time: %(end_time)r\n "
		        "location: %(location)r\n "
		        "status: %(status)r\n "
		        "description: %(description)r"
		        ">") % {
		      		'calendar_title': self.calendar_title,
		      		'event_title': self.event_title,
		      		'event_id': self.event_id,
		      		'start_time': self.start_time,
		      		'end_time': self.end_time,
		      		'location': self.location,
		      		'status': self.status,
		      		'description': self.description[:40]}
				
	def __eq__(self, other):
		return (
			self.calendar_title == other.calendar_title and
			self.event_title == other.event_title and
			self.event_id == other.event_id and
			self.start_time == other.start_time and
			self.end_time == other.end_time and
			self.location == other.location and
			self.status == other.status and
			self.description == other.description)
				

class EventDescription:
	"""Represents data embedded in a Google Calendar description."""
	
	def __init__(self, start_time=None, end_time=None, location="", status="", 
							 description=""):
		self.start_time = start_time #A datetime.
		self.end_time = end_time #A datetime.
		self.location = location
		self.status = status
		self.description = description
		
	def __repr__(self):
		return ("<start time: %r end time: %r location: %s status: %s "
						"description: %s>") % (
		    self.start_time, self.end_time, self.location, self.status, 
		    self.description)
		
	def __eq__(self, other):
		return (self.start_time == other.start_time and 
						self.end_time == other.end_time and
						self.location == other.location and
						self.status == other.status and
						self.description == other.description)
		

NAMESPACE = "{http://www.w3.org/2005/Atom}"
ENTRY_TAG = NAMESPACE + "entry"
TITLE_TAG = NAMESPACE + "title"
CONTENT_TAG = NAMESPACE + "content"
ID_TAG = NAMESPACE + "id"

DESCRIPTION_STATUS_RE = re.compile(r'''Event Status:(?P<status>(\s+\w+)+)''')
assert DESCRIPTION_STATUS_RE
DESCRIPTION_WHERE_RE = re.compile(r'''Where:(?P<location>(\s+\w+)+)''')
assert DESCRIPTION_WHERE_RE
DESCRIPTION_WHEN_RE = re.compile(r'''When: (?P<when>[^<]+)''')
assert DESCRIPTION_WHEN_RE

class ParseError(Exception): pass

def parse_dates(when):
	"""Parses a Google Calendar when annotation."""
	start_string, end_string = when.split(" to ", 1)
	start_format = "%a %b %d, %Y %I"
	if ':' in start_string:
		start_format += ":%M"
	start_format += "%p"
	
	end_format = ""
	if ',' in end_string:
		end_format += "%a %b %d, %Y "
	end_format += "%I"
	if ':' in end_string:
		end_format += ":%M"
	end_format += "%p %Z"
	start = datetime.datetime.strptime(start_string, start_format)
	end = datetime.datetime.strptime(end_string, end_format)
	end = datetime.datetime(start.year, start.month, start.day, end.hour, 
													end.minute)
	return start, end

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
	when = DESCRIPTION_WHEN_RE.search(meta)
	if not when:
		print "Couldn't find when in %r" % meta 
		raise ParseError()
	when = when.groupdict()
	when = when["when"].strip()
	start_time, end_time = parse_dates(when)
	where = DESCRIPTION_WHERE_RE.search(meta)
	if where:
		where = where.groupdict()
		location = where["location"].strip()
	else:
		location = None
	status = DESCRIPTION_STATUS_RE.search(meta)
	if not status:
		raise ParseError()
	status = status.groupdict()
	event_status = status["status"].strip()
	return EventDescription(start_time=start_time, end_time=end_time, 
													location=location, status=event_status, 
													description=description)
	    

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
  
  event_description = parse_description(contenttag.text)
  
  return Event(calendar_title=cal_title, event_id=id_key,
  						 event_title=titletag.text, 
  						 start_time=event_description.start_time,
  						 end_time=event_description.end_time,
  						 location=event_description.location,
  						 status=event_description.status,
  						 description=event_description.description)

def parse_feed(xml):
	feed = ET.parse(xml)
	cal_title = feed.find(TITLE_TAG)
	entries = feed.findall(ENTRY_TAG)
	return [make_event(entry, cal_title.text) for entry in entries]
		