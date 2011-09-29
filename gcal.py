# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: interface with calendar server, parse calendar responses, 
# produce useful event objects.

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
				self.calendar_title, self.event_id, self.event_title, self.description)

NAMESPACE = "{http://www.w3.org/2005/Atom}"
ENTRY_TAG = NAMESPACE + "entry"
TITLE_TAG = NAMESPACE + "title"
CONTENT_TAG = NAMESPACE + "content"
ID_TAG = NAMESPACE + "id"


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
	for entry in entries:
		print make_event(entry, cal_title.text)
		
  	
parse_feed("calendar.xml")