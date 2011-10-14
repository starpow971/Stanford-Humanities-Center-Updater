#!/usr/bin/env python
# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Scott Williams <scottw@artesiancode.com>
# Description: A shim over the filesystem so we can avoid clobbering files we
# don't own.

import unittest

import file_manager

class FileManagerTest(unittest.TestCase):
  def testMakeArchivedFilename(self):
    fm = file_manager.FileManager()
    self.assertEquals(".foo.bak", fm._ArchivedFile("foo"))
    self.assertEquals("bar/.foo.bak", fm._ArchivedFile("bar/foo"))
    self.assertEquals("/bar/.foo.bak", fm._ArchivedFile("/bar/foo"))
    self.assertEquals(".foo.html.bak", fm._ArchivedFile("foo.html"))

if __name__ == '__main__':
  unittest.main()
