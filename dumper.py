# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: Dump events from calendar and tumblr feeds straight into database.


import urllib2

import datastore
import gcal
import tumblr

calendar_ids = {
  "shc": "stanford.humanities.events%40gmail.com",
  "archaeology today": "8lg8kfefafh0o78nf0aaks144k%40group.calendar.google.com",
  "art as documentation": "giajfek5u3eadsh0kubm4ujapk%40group.calendar.google.com",
  "cognition language": "qt64bvm60aqgtcnt7dplsq1rds%40group.calendar.google.com",
  "context dependence": "78v8iihj2d3f0h6l6260qoric8%40group.calendar.google.com",
  "ethics politics": "61bjb0uj27vtoq2ueo4fcv609g%40group.calendar.google.com",
  "gnp": "1o8jo65ni7npb02l2kfvi9sibg%40group.calendar.google.com",
  "interdisciplinary approaches": "bfvev6s9081o7c7vodtp4snbj8@group.calendar.google.com",
  "modern middle east": "5e85ft4r0lkrmkj1lqic1dsejk@group.calendar.google.com",
  "mythos and logos": "fosbsf1alk8nc6baua1vkimlao@group.calendar.google.com",
  "prg": "fqm0j67ksqueq5lo100pq2c13c@group.calendar.google.com",
  "ser": "0a4j0vi87dlle6bjjkamr06tfs@group.calendar.google.com",
  "transamerican studies": "2l6d4g9kgomok6o311infg28c4@group.calendar.google.com",
  "vvlar": "db83bnp7ps0oq07t12qjujgsdc@group.calendar.google.com",
  "visualizing complexity": "sal6d7mo9rj3l9knn8ot9l69rg@group.calendar.google.com",
  "working group on the novel": "5a7sgmn064v1jsif3uln6lqf3s@group.calendar.google.com",
  "poetics": "ht02jaieajfqdkqogpcsso40cs@group.calendar.google.com"
}

events = []
for calendar_id in calendar_ids.itervalues():
  url = ("https://www.google.com/calendar/feeds/" + calendar_id + "/public/basic?"
         "showdeleted=true&updated-min=2011-08-01T01:00:00-08:00&max-results=1000")
  events += gcal.parse_feed(urllib2.urlopen(url))

news = tumblr.parse_rss(urllib2.urlopen("http://stanfordhumanitiescenter.tumblr.com/rss"))

store = datastore.load("database.db")
store.update(events, news)
store.save()
store.close()
