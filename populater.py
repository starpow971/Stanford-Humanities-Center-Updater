# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: Pulls events from database and writes them to disc.

import datetime

import datastore
import file_manager

fm = file_manager.FileManager()
ds = datastore.DataStore("database.db")

start_date = datetime.datetime.now()
end_date = start_date + datetime.timedelta(31)

events = ds.GetEventsInRange(start_date, end_date)

for event in events:
  print event
