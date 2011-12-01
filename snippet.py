#!/usr/bin/env python
# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE.
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: Creates a snippet for the blogs; used in the news-template.

import re


def strip_tags(html):
  return re.sub('<[^<]+?>', '', html)

_TABLE_RE = re.compile('<table.*</table>', re.DOTALL)

def prune_images(html):
  return _TABLE_RE.sub('', html)

def Snippet(content):
  content = prune_images(content)
  content = strip_tags(content)
  words = content.split(' ')
  snippet = ' '.join(words[:100])
  return snippet