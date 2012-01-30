#!/usr/bin/env python
# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE.
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: Configure calendar titles.

import collections

CalendarConfig = collections.namedtuple(
  "CalendarConfig",
  ["calendar_name",  # Human readable calendar name
   "calendar_id",  # Google Calendar ID
    "landing_page_template", # Which template file to use for the landing page
   ])

calendar_ids = [
  CalendarConfig(calendar_name="Stanford Humanities Center Events",
                 calendar_id="stanford.humanities.events%40gmail.com",
                 landing_page_template="calendar-landing-page.tmpl"),
  CalendarConfig(calendar_name="Archaeology Today",
                 calendar_id="8lg8kfefafh0o78nf0aaks144k%40group.calendar.google.com",
                 landing_page_template="workshop-landing-page.tmpl"),
  CalendarConfig(calendar_name="Art as Documentation, Memory as Art",
                 calendar_id="giajfek5u3eadsh0kubm4ujapk%40group.calendar.google.com",
                 landing_page_template="workshop-landing-page.tmpl"),
  CalendarConfig(calendar_name="Co-sponsored Events Held at the Humanities Center",
                 calendar_id="otvj0o3d1s8kao8ohg9t4o958s@group.calendar.google.com",
                 landing_page_template="calendar-landing-page.tmpl"),
  CalendarConfig(calendar_name="Cognition & Language",
                 calendar_id="qt64bvm60aqgtcnt7dplsq1rds%40group.calendar.google.com",
                 landing_page_template="workshop-landing-page.tmpl"),
  CalendarConfig(calendar_name="Context Dependence in Language and Communication",
                 calendar_id="78v8iihj2d3f0h6l6260qoric8%40group.calendar.google.com",
                 landing_page_template="workshop-landing-page.tmpl"),
  CalendarConfig(calendar_name="Ethics & Politics, Ancient & Modern",
                 calendar_id="61bjb0uj27vtoq2ueo4fcv609g%40group.calendar.google.com",
                 landing_page_template="workshop-landing-page.tmpl"),
  CalendarConfig(calendar_name="Graphic Narrative Project",
                 calendar_id="1o8jo65ni7npb02l2kfvi9sibg%40group.calendar.google.com",
                 landing_page_template="workshop-landing-page.tmpl"),
  CalendarConfig(calendar_name="Interdisciplinary Approaches to Consciousness",
                 calendar_id="bfvev6s9081o7c7vodtp4snbj8@group.calendar.google.com",
                 landing_page_template="workshop-landing-page.tmpl"),
  CalendarConfig(calendar_name="Modern Middle East",
                 calendar_id="5e85ft4r0lkrmkj1lqic1dsejk@group.calendar.google.com",
                 landing_page_template="workshop-landing-page.tmpl"),
  CalendarConfig(calendar_name="Mythos and Logos: Religion and Rationality in the Humanities",
                 calendar_id="fosbsf1alk8nc6baua1vkimlao@group.calendar.google.com",
                 landing_page_template="workshop-landing-page.tmpl"),
  CalendarConfig(calendar_name="Philosophical Reading Group",
                 calendar_id="fqm0j67ksqueq5lo100pq2c13c@group.calendar.google.com",
                 landing_page_template="workshop-landing-page.tmpl"),
  CalendarConfig(calendar_name="Seminar on Enlightenment and Revolution, 1660-1830",
                 calendar_id="0a4j0vi87dlle6bjjkamr06tfs@group.calendar.google.com",
                 landing_page_template="workshop-landing-page.tmpl"),
  CalendarConfig(calendar_name="Test SHC Calendar",
                 calendar_id="nbeb5t20heagh1j60uq3u2522o@group.calendar.google.com",
                 landing_page_template="calendar-landing-page.tmpl"),
  CalendarConfig(calendar_name="Test Workshop Calendar",
                 calendar_id="tn7oa03ign9gpenk8aii7oit44@group.calendar.google.com",
                 landing_page_template="workshop-landing-page.tmpl"),
  CalendarConfig(calendar_name="TransAmerican Studies",
                 calendar_id="2l6d4g9kgomok6o311infg28c4@group.calendar.google.com",
                 landing_page_template="workshop-landing-page.tmpl"),
  CalendarConfig(calendar_name="Verbal and Visual Literacies of Ancient Rome",
                 calendar_id="db83bnp7ps0oq07t12qjujgsdc@group.calendar.google.com",
                 landing_page_template="workshop-landing-page.tmpl"),
  CalendarConfig(calendar_name="Visualizing Complexity and Uncertainty: Exploring Humanistic "
                               "Approaches to Graphic Representation",
                 calendar_id="sal6d7mo9rj3l9knn8ot9l69rg@group.calendar.google.com",
                 landing_page_template="workshop-landing-page.tmpl"),
  CalendarConfig(calendar_name="Working Group on the Novel",
                 calendar_id="5a7sgmn064v1jsif3uln6lqf3s@group.calendar.google.com",
                 landing_page_template="workshop-landing-page.tmpl"),
  CalendarConfig(calendar_name="Workshop in Poetics",
                 calendar_id= "ht02jaieajfqdkqogpcsso40cs@group.calendar.google.com",
                 landing_page_template="workshop-landing-page.tmpl")
]
