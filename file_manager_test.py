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
    self.assertEquals(".foo.bak", fm._archived_file("foo"))
    self.assertEquals("bar/.foo.bak", fm._archived_file("bar/foo"))
    self.assertEquals("/bar/.foo.bak", fm._archived_file("/bar/foo"))
    self.assertEquals(".foo.html.bak", fm._archived_file("foo.html"))

  def testArchiveAlreadyArchived(self):
    called_rename = False
    def CallRename(src, dest):
      called_rename = True

    fm = file_manager.FileManager(path_checker=lambda fn: True,
                                  file_mover=CallRename)
    fm.archive("foo")
    self.assertFalse(called_rename)

  def testArchiveMovesStuff(self):
    rename_args = {}
    def CallRename(*args):
      rename_args['foo'] = args

    fm = file_manager.FileManager(path_checker=lambda fn: False,
                                  file_mover=CallRename)
    fm.archive("foo")
    self.assertEquals(("foo", ".foo.bak"), rename_args['foo'])

  class RecordingReader:
    def __init__(self, value):
      self.args = None
      self.value = value

    def read(self, *args):
      self.args = args
      return self.value

  def testReadUnarchived(self):
    r = self.RecordingReader("content")
    fm = file_manager.FileManager(path_checker=lambda fn: False, reader=r.read)
    self.assertEquals("content", fm.read("foo"))
    self.assertEquals(("foo",), r.args)

  def testReadArchived(self):
    r = self.RecordingReader("content")
    fm = file_manager.FileManager(path_checker=lambda fn: True, reader=r.read)
    fm.archive("foo")
    self.assertEquals("content", fm.read("foo"))
    self.assertEquals((".foo.bak",), r.args)

  def testDiff(self):
    fm = file_manager.FileManager(reader=lambda fn: fn + '-contents',
                                  path_checker=lambda fn: True)
    self.assertEquals("foo-contents", fm.read("foo"))
    fm.save("foo", "clobbered!")
    expected = ("M foo\n"
                "--- foo \n"
                "+++ foo \n"
                "@@ -1,1 +1,1 @@\n"
                "-foo-contents\n"
                "+clobbered!\n")
    self.assertEquals(expected, fm.show_diff())

  def testDiffNew(self):
    fm = file_manager.FileManager(path_checker=lambda fn: False)
    fm.save("foo", "clobbered!")
    expected = "A foo\n"
    self.assertEquals(expected, fm.show_diff())


if __name__ == '__main__':
  unittest.main()
