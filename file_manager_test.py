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
    class MockEnv:
      def __init__(self):
        self.called_rename = False

      def CheckPath(self, path):
        # Pretend we've already archived this file
        assert path == ".foo.bak"
        return True

      def RenameFile(self, src, dest):
        self.called_rename = True

    env = MockEnv()
    fm = file_manager.FileManager(env=env)
    fm.archive("foo")
    self.assertFalse(env.called_rename)

  def testArchiveMovesStuff(self):
    class MockEnv:
      def __init__(self):
        self.rename_args = None

      def MoveFile(self, src, dest):
        self.rename_args = src, dest

      def CheckPath(self, path):
        # Pretend we HAVEN'T already archived this file
        assert path == ".foo.bak"
        return False

    env = MockEnv()
    fm = file_manager.FileManager(env=env)
    fm.archive("foo")
    self.assertEquals(("foo", ".foo.bak"), env.rename_args)

  def testReadUnarchived(self):
    class MockEnv:
      def __init__(self):
        self.called_read = False

      def ReadFile(self, file):
        assert file == "foo"
        self.called_read = True
        return "file content"

    env = MockEnv()
    fm = file_manager.FileManager(env=env)
    self.assertEquals("file content", fm.read("foo"))
    self.assertTrue(env.called_read)

  def testReadArchived(self):
    class MockEnv:
      def __init__(self):
        self.called_read = False

      def CheckPath(self, file):
        # Pretend we've already archived this file
        assert file == ".foo.bak"
        return True

      def ReadFile(self, file):
        assert file == ".foo.bak"  # We'll read the archive if it exists.
        self.called_read = True
        return "file content"

    env = MockEnv()
    fm = file_manager.FileManager(env=env)
    fm.archive("foo")
    self.assertEquals("file content", fm.read("foo"))
    self.assertTrue(env.called_read)

  def testDiff(self):
    class MockEnv:
      def __init__(self):
        pass
      def ReadFile(self, file):
        assert file == "foo"
        return "Original contents"
      def CheckPath(self, file):
        assert file == "foo"
        return True

    env=MockEnv()
    fm = file_manager.FileManager(env=env)
    fm.save("foo", "New contents")
    expected = ("M foo\n"
                "--- foo \n"
                "+++ foo \n"
                "@@ -1,1 +1,1 @@\n"
                "-Original contents\n"
                "+New contents\n")
    self.assertEquals(expected, fm.show_diff())

  def testDiffNew(self):
    class MockEnv:
      def __init__(self):
        pass
      def ReadFile(self, file):
        assert False, "This method should never be called!"
      def CheckPath(self, file):
        assert file == "foo"
        return False
    env = MockEnv()
    fm = file_manager.FileManager(env=env)
    fm.save("foo", "clobbered!")
    expected = "A foo\n"
    self.assertEquals(expected, fm.show_diff())

  def testCommitDirectoryExists(self):
    test = self
    class MockEnv:
      def __init__(self):
        pass

      def CheckPath(self, path):
        test.assertEquals(".", path)
        return True

      def WriteFile(self, path, contents):
        assert path == "foo"
        assert contents == "contents"

    env = MockEnv()
    fm = file_manager.FileManager(env=env)
    fm.save("foo", "contents")
    fm.commit()

  def testCommitDirectoryDoesntExist(self):
    class MockEnv:
      def __init__(self):
        self.called_mkdir = False

      def CheckPath(self, path):
        assert path == "dir"
        return False

      def WriteFile(self, path, contents):
        assert path == "dir/foo"
        assert contents == "contents"

      def MakeDir(self, path):
        assert path == "dir"
        self.called_mkdir = True
        return True

    env = MockEnv()
    fm = file_manager.FileManager(env=env)
    fm.save("dir/foo", "contents")
    fm.commit()
    self.assertTrue(env.called_mkdir)


if __name__ == '__main__':
  unittest.main()
