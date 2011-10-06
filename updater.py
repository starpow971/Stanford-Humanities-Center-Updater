#This is a nonfunctional sketch

import datetime

import gcal
import tumblr
import datastore
import filemanager
import template

GCAL_URL = "www.example...."
TUMBLR_URL = "www.tumblr...."
DATASTORE_FILE = "datastorefile..."
UPCOMING_EVENTS_TEMPLATE = "events/calendar-mockup/index.html"
UPCOMING_EVENTS_PAGE = "events/calendar/index.html"
WHATS_NEW_TEMPLATE = "whats-new-mockup/index.html"
WHATS_NEW_PAGE = "whats-new/index.html"
POST_TEMPLATE = "whats-new-mockup-post/index.html"
EVENT_TEMPLATE = "events/calendar-mockup-event/index.html"
POST_FILE = "whats-new/%s.html"
EVENT_FILE = "events/calendar/%s.html"

def main(pretend=False, now=datetime.datetime.now()):
	fm = filemanager.FileManager()
	fm.moveouttheway(UPCOMING_EVENTS_TEMPLATE)
	fm.moveouttheway(WHATS_NEW_TEMPLATE)
	fm.moveouttheway(POST_TEMPLATE)
	fm.moveouttheway(EVENT_TEMPLATE)
	
	new_cal_entries = gcal.get_calendar_entries(GCAL_URL)
	new_blog_entries = tumblr.get_blog_entries(TUMBLR_URL)
	store = datastore.load(DATASTORE_FILE)
	store.update(new_cal_entries, new_blog_entries)
	store.save()
	store.close()
	
	upcoming_events_tpl = template.parse(fm.read(UPCOMING_EVENTS_TEMPLATE))
	upcoming_events = store.get_upcoming_events(now)
	upcoming_events_output = upcoming_events_tpl.render(upcoming_events)
	fm.save(UPCOMING_EVENTS_PAGE, upcoming_events_output)
	
	whats_new_tpl = template.parse(fm.read(WHATS_NEW_TEMPLATE))
	whats_new = store.get_whats_new(now)
	whats_new_output = whats_new_tpl.render(whats_new)
	fm.save(WHATS_NEW_PAGE, whats_new_output)
	
	post_tpl = template.parse(fm.read(POST_TEMPLATE))
	for post in store.get_blog_posts():
		post_output = post_tpl.render(post)
		fm.save(POST_FILE % post.title, post_output)
		
	event_tpl = template.parse(fm.read(EVENT_TEMPLATE))
	for event in store.get_events():
		event_output = event_tpl.render(event)
		fm.save(EVENT_FILE % event.title, event_output)
		
	if pretend:
		fm.show_diff()
	else:
		fm.commit()