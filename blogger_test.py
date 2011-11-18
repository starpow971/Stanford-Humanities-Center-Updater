#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE.
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: interface with blogger server, parse blogger responses,
# produce useful blog objects.

import datetime
import unittest

import blogger

class BloggerTest(unittest.TestCase):
  def testParsePostDate(self):
    published = blogger.parse_date("2011-10-28T16:51:00.000-07:00")
    self.assertEquals(datetime.datetime(2011, 10, 28, 16, 51), published)

if __name__ == '__main__':
  unittest.main()
