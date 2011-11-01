#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE.
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: interface with tumblr server, parse tumblr responses,
# produce useful blog objects.

import xml.etree.ElementTree as ET
import datetime
import logging

class Post:
  """Represents a Tumblr blog post."""

  def __init__(self, post_title="", post_date="", post_content="", post_category="", post_id=0):
    self.post_title = post_title
    self.post_date = post_date
    self.post_content = post_content
    self.post_category = post_category
    self.post_id = post_id

  def __repr__(self):
    return "<title: '%r' date: '%r' post: '%r' category: '%r' id: '%r'>" % (
      self.post_title, self.post_date, self.post_content, self.post_category, self.post_id)

ITEM_TAG = "channel/item"
TITLE_TAG = "title"
DESCRIPTION_TAG = "description"
DATE_TAG = "pubDate"
CATEGORY_TAG = "category"
GUID_TAG = "guid"


def make_post(item):
  titletag = item.find(TITLE_TAG)
  if titletag is None:
    logging.warning("No title tag found in %s" % item)
    return

  descriptiontag = item.find(DESCRIPTION_TAG)
  if descriptiontag is None:
    logging.warning("No description tag found in %s" % item)
    return

  datetag = item.find(DATE_TAG)
  if datetag is None:
    logging.warning("No date tag found in %s" % item)
    return

  categorytag = item.find(CATEGORY_TAG)
  if categorytag is None:
    category = None
  else:
    category = categorytag.text

  idtag = item.find(GUID_TAG)
  if idtag is None:
    logging.warning("No guid tag found in %s" % item)
    return

  return Post(post_title=titletag.text,
              post_date=parse_time(datetag.text.encode('ascii', 'ignore')),
              post_content=descriptiontag.text, post_category=category,
              post_id=int(idtag.text.rsplit("/", 1)[1]))

def parse_time(s):
  timestr, _ = s.rsplit(' ', 1)
  return datetime.datetime.strptime(timestr, "%a, %d %b %Y %H:%M:%S")

def parse_rss(xml):
  rss = ET.parse(xml)
  items = rss.findall(ITEM_TAG)
  return [make_post(item) for item in items]

#import pdb; pdb.set_trace()
#print parse_rss("tumblr.xml")
