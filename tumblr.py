# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: interface with tumblr server, parse tumblr responses, 
# produce useful blog objects.

import xml.etree.ElementTree as ET

class Blog:
	"""Represents a Tumblr blog post."""
	
	def __init__(self, post_title="", post_date=None, post_content="", post_category=""):
		self.post_title = post_title
		self.post_date = post_date
		self.post_content = post_content
		self.post_category = post_category
		
	def __repr__(self):
		return "<title: '%s' date: '%s' post: '%s' category: '%s'>" % (
			self.post_title, self.post_date, self.post_content [40], self.post_category)
			
NAMESPACE = "{http://www.w3.org/2005/Atom}"
ITEM_TAG = NAMESPACE + "item"
TITLE_TAG = NAMESPACE + "title"
DESCRIPTION_TAG = NAMESPACE + "description"
DATE_TAG = NAMESPACE + "pubDate"
CATEGORY_TAG = NAMESPACE + "category"


def make_post(item):
	titletag = item.find(TITLE_TAG)
	if titletag is None:
		#todo: log an error
		return
		
	descriptiontag = item.find(DESCRIPTION_TAG)
	if descriptiontag is None:
		#todo: log an error
		return
			
	datetag = item.find(DATE_TAG)
	if datetag is None:
		#todo: log an error
		return
	
	categorytag = item.find(CATEGORY_TAG)
			
	return Blog(post_title=titletag.text, post_date=datetag.text, post_content=descriptiontag.text, post_category=categorytag.text)
	
def parse_rss(xml):
	rss = ET.parse(xml)
	items = rss.findall(ITEM_TAG)
	for item in items:
		print make_post(item)
		
parse_rss("tumblr.xml")