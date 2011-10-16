# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Scott Williams <scottw@artesiancode.com>
# Description: A shim over the filesystem so we can avoid clobbering files we
# don't own.

import difflib
import os

class FileManager:
  """Represents pending changes to the filesystem."""

  class Env:
    """Abstracts away filesystem operations to allow easy testing."""
    def ReadFile(self, filename):
      with open(filename) as f:
        return f.read()

    def WriteFile(self, filename, contents):
      with open(filename, 'w') as f:
        f.write(contents)

    def MoveFile(self, src, dest):
      return os.rename(src, dest)

    def CheckPath(self, path):
      return os.path.exists(path)

    def MakeDir(self, path):
      return os.mkdirs(path)

  def __init__(self, env=Env()):
    self.env = env
    self.archives = {}
    self.files = {}

  def _archived_file(self, filename):
    """Given a regular filename, returns the archived name."""
    dir, base = os.path.split(filename)
    if dir:
      return "%s/.%s.bak" % (dir, base)
    else:
      return ".%s.bak" % base

  def archive(self, filename):
    """Makes sure a template file won't be clobbered.
    
    If a file named .<filename>.bak exists, this method has no effect. Otherwise
    it moves the named file.
    """
    archived_filename = self._archived_file(filename)
    self.archives[filename] = archived_filename
    if self.env.CheckPath(archived_filename):
      # File was already moved!
      return
    self.env.MoveFile(filename, archived_filename)

  def read(self, filename):
    """Reads a file from the filesystem.

    Why not just use read? Well, Archive might have moved it!"""
    return self.env.ReadFile(self.archives.get(filename, filename))

  def save(self, filename, contents):
    """Saves a file. Doesn't touch the filesystem."""
    assert filename not in self.archives, "Attempt to overwrite an archive"
    self.files[filename] = contents

  def show_diff(self):
    """Shows changes you have made to the filesystem."""
    summary = ""
    diffs = ""
    for filename, content in sorted(self.files.iteritems()):
      if not self.env.CheckPath(self.archives.get(filename, filename)):
        summary += "A %s\n" % filename
        continue
      original_content = self.env.ReadFile(filename)
      if content != original_content:
        summary += "M %s\n" % filename
        diffs += ''.join(difflib.unified_diff(
                              [l + '\n' for l in original_content.split('\n')],
                              [l + '\n' for l in content.split('\n')],
                              filename, filename))
    return summary + diffs

  def commit(self):
    """Writes your changes to disk."""
    dirs = set([os.path.dirname(file) for file in self.files.iterkeys()])
    if "" in dirs:
      # path.dirname is silly and returns "" for the current directory.
      dirs.remove("")
      dirs.add(".")
    for dir in dirs:
      if not self.env.CheckPath(dir):
        self.env.MakeDir(dir)
    for filename, content in self.files.iteritems():
      self.env.WriteFile(filename, content)
