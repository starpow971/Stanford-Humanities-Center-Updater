# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Scott Williams <scottw@artesiancode.com>
# Description: A shim over the filesystem so we can avoid clobbering files we
# don't own.

class FileManager:
  def moveouttheway(self, filename):
    """Makes sure a template file won't be clobbered."""
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
