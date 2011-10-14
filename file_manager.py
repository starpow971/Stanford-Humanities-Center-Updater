# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Scott Williams <scottw@artesiancode.com>
# Description: A shim over the filesystem so we can avoid clobbering files we
# don't own.

import difflib
import os

def _ReadFile(filename):
  with open(filename) as f:
    return f.read()

def _WriteFile(filename, contents):
  with open(filename, 'w') as f:
    f.write(contents)

class FileManager:
  def __init__(self, path_checker=os.path.exists, file_mover=os.rename,
               reader=_ReadFile):
    self.check_path = path_checker
    self.move_file = file_mover
    self.read_file = reader
    self.archives = {}
    self.files = {}

  def _ArchivedFile(self, filename):
    """Given a regular filename, returns the archived name."""
    dir, base = os.path.split(filename)
    if dir:
      return "%s/.%s.bak" % (dir, base)
    else:
      return ".%s.bak" % base

  def Archive(self, filename):
    """Makes sure a template file won't be clobbered.
    
    If a file named .<filename>.bak exists, this method has no effect. Otherwise
    it moves the named file.
    """
    archived_filename = self._ArchivedFile(filename)
    self.archives[filename] = archived_filename
    if self.check_path(archived_filename):
      # File was already moved!
      return
    self.move_file(filename, archived_filename)

  def read(self, filename):
    """Reads a file from the filesystem.

    Why not just use read? Well, moveouttheway might have moved it!"""
    return self.read_file(self.archives.get(filename, filename))

  def save(self, filename, contents):
    """Saves a file. Doesn't touch the filesystem."""
    assert filename not in self.archives, "Attempt to overwrite an archive"
    self.files[filename] = contents

  def show_diff(self):
    """Shows changes you have made to the filesystem."""
    diffs = ""
    for filename, content in self.files.iteritems():
      original_content = self.read_file(filename)
      if content != original_content:
        diffs += ''.join(difflib.unified_diff(
                              [l + '\n' for l in original_content.split('\n')],
                              [l + '\n' for l in content.split('\n')],
                              filename, filename))
    return diffs

  def commit(self):
    """Writes your changes to disk."""
    for filename, content in self.files.iteritems():
      self.write_file(filename, content)
