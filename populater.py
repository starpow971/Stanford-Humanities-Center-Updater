#!/usr/bin/env python
# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: Pulls events from database and writes them to disc.


from Cheetah.Template import Template
from optparse import OptionParser
import datetime
import sys

import datastore
import file_manager

def parse_args(argv):
  """Sets up the option parser and parses command line arguments.

  Returns:
    options, args: a pair whose first element is an Options object with settings
    taken from the command line, and whose second element is the remaining
    unparsed arguments on the command line.
  """
  op = OptionParser()
  op.add_option("-o", "--output-dir", dest="output_dir",
                help="Output generated files under DIR",
                metavar="DIR",
                default="/Library/Server/Web/Data/Sites/Default/")
  options, args = op.parse_args(argv[1:])
  if not options.output_dir.endswith("/"):
    options.output_dir += "/"
  return options, args


def main(argv):
  options, args = parse_args(argv)
  fm = file_manager.FileManager()
  ds = datastore.DataStore("database.db")

  start_date = datetime.datetime.now()
  end_date = start_date + datetime.timedelta(31)

  # NOTE(scottrw): the list() function is necessary because GetEventsInRange
  # returns a generator, which is exhausted by the first template, leaving no
  # events left for the second template!
  events = list(ds.GetEventsInRange(start_date, end_date))

  fm.save(options.output_dir + "events/calendar/index.html",
          str(Template(file="calendar-landing-page.tmpl",
                       searchList=[{"events": events}])))

  fm.save(options.output_dir + "workshops/calendar/index.html",
          str(Template(file="workshop-landing-page.tmpl",
                       searchList=[{"events": events}])))

  print fm.show_diff()
  fm.commit()

if __name__ == "__main__":
  main(sys.argv)
