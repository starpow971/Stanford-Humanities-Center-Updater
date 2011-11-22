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

  def uri(self):
    return "news-videos/news/%s-%s-%s-%s.html" % (self.published.year,
            self.published.month, self.published.day, self.friendly_title())

  def friendly_title(self):
    title = re.sub(" +", "-", self.title.lower())
    title = re.sub("[^-a-z0-9]", "", title)
    return title

  def yearmonth(self):
    return datetime.datetime(self.published.year, self.published.month, 1)

  def __repr__(self):
    return ("\n<id: %(id)r\n "
            "updated: %(updated)r\n "
            "title: %(title)r\n "
            "published: %(published)r\n "
            "content: %(content)r\n "
            "categories: %(categories)r\n "
            "summary: %(summary)r\n "
            ">") % {
              'id': self.id,
              'updated': self.updated,
              'title': self.title,
              'published': self.published,
              'content': self.content,
              'categories': self.categories,
              'summary': self.summary}

def GetPosts():
  client = gdata.blogger.client.BloggerClient()
  gdata_posts = client.GetPosts("3248988153222732762")
  return [MakePost(post) for post in gdata_posts.entry]


def MakePost(gdata_post):
  pub_date = parse_date(gdata_post.published.text)
  updated_date = gdata_post.updated.text
  return Post(content=gdata_post.content.text, published=pub_date,
              summary=gdata_post.summary,
              categories=", ".join([c.term for c in gdata_post.category]), id=parse_id(gdata_post),
              title=gdata_post.title.text, updated=updated_date)


def parse_date(date):
  date_format = "%Y-%m-%dT%H:%M:%S"
  date, weird_thing = date.split(".", 1)
  date = datetime.datetime.strptime(date.encode('ascii', 'ignore'), date_format)
  return date

def parse_id(gdata_post):
  id = gdata_post.id.text
  id_text, id = id.split("post-", 1)
  id = int(id)
  return id
