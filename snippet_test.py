#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE.
# Author: Christine Williams <christine.bennett.williams@gmail.com>


import unittest

import snippet

class SnippetTest(unittest.TestCase):
  def testParseWithImage(self):
    img_snp = snippet.Snippet("2011-10-28T16:51:00.000-07:00")
    self.assertEquals(datetime.datetime(2011, 10, 28, 16, 51), published)

if __name__ == '__main__':
  unittest.main()
