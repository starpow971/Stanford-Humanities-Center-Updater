#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE.
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: interface with blogger server, parse blogger responses,
# produce useful blog objects.

import gdata.blogger.client
import datetime
import pprint

class Post:
  def __init__(self, content="", published=None, summary="", categories="",
               id="", title="", updated=None):
    self.content = content
    self.published = published
    self.summary = summary
    self.categories = categories
    self.id = id
    self.title = title
    self.updated = updated

def GetPosts():
  client = gdata.blogger.client.BloggerClient()
  gdata_posts = client.GetPosts("3248988153222732762")
  return [MakePost(post) for post in gdata_posts.entry]


def MakePost(gdata_post):
  pub_date = parse_date(gdata_post.published.text)
  updated_date = parse_date(gdata_post.updated.text)
  return Post(content=gdata_post.content, published=pub_date,
              summary=gdata_post.summary,
              categories=", ".join([c.term for c in gdata_post.category]), id=gdata_post.id,
              title=gdata_post.title, updated=updated_date)


def parse_date(date):
  date_format = "%Y-%m-%dT%H:%M:%S"
  date, weird_thing = date.split(".", 1)
  date = datetime.datetime.strptime(date.encode('ascii', 'ignore'), date_format)
  return date
