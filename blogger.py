#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE.
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: interface with blogger server, parse blogger responses,
# produce useful blog objects.

import gdata.blogger.client

class Post:
  def __init__(self, content="", published=None, summary="", categories=""
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
  return [MakePost(post) for post in gdata_posts]



def MakePost(gdata_post):
  return Post(content=content, published=published, summary=summary,
              categories=categories, id=id, title=title, updated=updated)

