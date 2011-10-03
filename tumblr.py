#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: interface with tumblr server, parse tumblr responses, 
# produce useful blog objects.

import xml.etree.ElementTree as ET

class Blog:
	"""Represents a Tumblr blog post."""
	
	def __init__(self, post_title="", post_date="", post_content="", post_category=""):
	#todo: fix ASCII encoding problem.
		self.post_title = post_title
		self.post_date = post_date
		self.post_content = post_content
		self.post_category = post_category
		
	def __repr__(self):
		return "<title: '%r' date: '%r' post: '%r' category: '%r'>" % (
			self.post_title, self.post_date, self.post_content, self.post_category)
			
ITEM_TAG = "channel/item"
TITLE_TAG = "title"
DESCRIPTION_TAG = "description"
DATE_TAG = "pubDate"
CATEGORY_TAG = "category"


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
	if categorytag is None:
	  category = None
	else:
	  category = categorytag.text
			
	return Blog(post_title=titletag.text, post_date=datetag.text, 
	            post_content=descriptiontag.text, post_category=category)
	
def parse_rss(xml):
	rss = ET.parse(xml)
	items = rss.findall(ITEM_TAG)
	for item in items:
		print make_post(item)
		
#import pdb; pdb.set_trace()
parse_rss("tumblr.xml")
