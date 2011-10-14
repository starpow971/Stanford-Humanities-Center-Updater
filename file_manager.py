# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Scott Williams <scottw@artesiancode.com>
# Description: A shim over the filesystem so we can avoid clobbering files we
# don't own.

import os

class FileManager:
  def __init__(self, path_checker=os.path.exists):
    self.check_path = path_checker

  def _ArchivedFile(self, filename):
    dir, base = os.path.split(filename)
    if dir:
      return "%s/.%s.bak" % (dir, base)
    else:
      return ".%s.bak" % base

  def moveouttheway(self, filename):
    """Makes sure a template file won't be clobbered.
    
    If a file named .<filename>.bak exists, this method has no effect. Otherwise
    it moves the named file.
    """
    # if self.check_path(
    pass

  def read(self, filename):
    """Reads a file from the filesystem.

    Why not just use read? Well, moveouttheway might have moved it!"""
    pass

  def save(self, filename, contents):
    """Saves a file. Doesn't touch the filesystem."""
    pass

  def show_diff(self):
    """Shows changes you have made to the filesystem."""
    pass

  def commit(self):
    """Writes your changes to disk."""
    pass
