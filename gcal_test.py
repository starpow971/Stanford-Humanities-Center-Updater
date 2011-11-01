#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: interface with calendar server, parse calendar responses, 
# produce useful event objects.

import datetime
import unittest

import gcal



# Test data from https://www.google.com/calendar/feeds/
# stanford.humanities.events%40gmail.com/public/full
# ?v=2&alt=jsonc&showdeleted=true
description1 = """
When: Thu Oct 13, 2011 1:30pm to 3:30pm 
PDT<br />

<br />Where: Stanford Humanities Center Board Room
<br />Event Status: confirmed
<br />Event Description: Adams Bodomo will.

thumbnail: https://picasaweb.google.com/104570033566114852437/201112SHCEvents#5659410196645602930

full_image: https://picasaweb.google.com/104570033566114852437/201112SHCEvents#5659410456066390706"""

description2 = """
When: Wed Nov 9, 2011 4pm to 6pm 
PST<br />

<br />Where: Humanities Center Board Room
<br />Event Status: confirmed
<br />Event Description: Helen Whitney is an award-winning filmmaker with over thirty years of experience producing dramatic features and documentary films. Her subjects have stretched across a broad spectrum of topics including youth gangs; a portrait of the 1996 Presidential candidates; a Trappist monastery in Massachusetts; the McCarthy Era; Pope John Paul II; and photographer Richard Avedon.

Helen Whitney and Marilyn Yalom will discuss Whitney’s work.

Marilyn Yalom is a senior scholar at the Michelle R. Clayman Institute for Gender Research, a former professor, and author of  &quot;A History of the Wife,&quot; &quot;Birth of the Chess Queen,&quot; and &quot;The American Resting Place.&quot;"""

description3 = """
When: Tue Oct 11, 2011 4pm to Tue Oct 11, 2011 6pm
PDT<br />
<br />Where: Stanford Humanities Center Board Room
<br />Event Status: confirmed
<br />Event Description: SiCa-Humanites Center Arts writer/practitioner M.K. Raina in conversation with Asst. Drama Professor Jisha Menon: 

Salon featuring M.K. Raina
  
Raina will discuss his creative work in theatre, experimental and mainstream cinema, and documentary film. He will discuss his role as founder and member of Sahmat, a cultural NGO, formed in the wake of the assassination of street theatre activist, Safdar Hashmi. He will also address his cultural activism in Kashmir: his work with the folk Bhand performers, with the rehabilitation of orphaned Kashmiri children, and with the setting up of educational opportunities for performers (especially children) in the Kashmir Valley. 

M.K. Raina is one of the most distinguished theatre practitioners in India today. He is a graduate of India’s premier theatre institution, the National School of Drama based in New Delhi and his unique talents have been recognized by India’s highest awards, including the B.V. Karanth Award for Lifetime Achievement in Theatre in 2007. One of the few Indian artists who tackles the complex questions of human rights, democracy, and militant terror in the Kashmir valley--his birthplace--his work is informed by his dynamic engagement in secular activism and ranges from Kashmiri folk theatre (working with the Bhand Pather, Kashmiri folk performers) to classical Hindustani and avant-garde cinema. He was nominated by the Centre for South Asia. M.K. Raina will be present on campus during the month of October 2011.

Please RSVP to Rachel Knowles- rknowles@stanford.edu.

Please consult the Center for South Asia for additional events related to M.K. Raina&#39;s residency."""

description4 = """
When: Wed Nov 2, 2011 4pm to Wed Nov 2, 2011 6pm 
PDT<br />

<br />Where: Stanford Humanities Center Levinthal Hall
<br />Event Status: confirmed
<br />Event Description: Alastair Macaulay, chief dance critic of &#39;The New York Times&#39; and former chief theatre critic for &#39;The Financial Times&#39;, has written in the past year about the movie &#39;Black Swan&#39;, about Grand Central Station as choreography, and about the artist Degas&#39;s depictions of ballet in painting and sculpture. He speaks about reviewing the performing arts today within a wider cultural framework.
When: Tue Aug 16, 2011 3pm to Tue Aug 16, 2011 7:30pm 
PDT<br />


<br />Event Status: confirmed
"""


class GcalTest(unittest.TestCase):
  def testParseDateAllDay(self):
    start, end, allday = gcal.parse_dates("Thu Oct 13, 2011")
    self.assertEquals(start, datetime.datetime(2011, 10, 13))
    self.assertEquals(end, datetime.datetime(2011, 10, 13))
    self.assertTrue(allday)
    
  def testParseDateSimple(self):
    start, end, allday = gcal.parse_dates("Thu Oct 13, 2011 1:30pm to 3:30pm PDT")
    self.assertEquals(start, datetime.datetime(2011, 10, 13, 13, 30))
    self.assertEquals(end, datetime.datetime(2011, 10, 13, 15, 30))
    
  def testParseDateSimpleNoMin(self):
    start, end, allday = gcal.parse_dates("Thu Oct 13, 2011 1pm to 3pm PDT")
    self.assertEquals(start, datetime.datetime(2011, 10, 13, 13))
    self.assertEquals(end, datetime.datetime(2011, 10, 13, 15))
    
  def testParseDateFullNoMin(self):
    start, end, allday = gcal.parse_dates(
        "Tue Oct 11, 2011 4pm to Tue Oct 11, 2011 6pm PDT")
    self.assertEquals(start, datetime.datetime(2011, 10, 11, 16))
    self.assertEquals(end, datetime.datetime(2011, 10, 11, 18))
    
  def testParseDateFullMin(self):
    start, end, allday = gcal.parse_dates(
        "Tue Oct 11, 2011 4:30pm to Tue Oct 11, 2011 6:30pm PDT")
    self.assertEquals(start, datetime.datetime(2011, 10, 11, 16, 30))
    self.assertEquals(end, datetime.datetime(2011, 10, 11, 18, 30))
    
  def testDescription(self):
    description = gcal.parse_description(description1)
    expected = gcal.EventDescription(
        start_time = datetime.datetime(2011, 10, 13, 13, 30),
        end_time = datetime.datetime(2011, 10, 13, 15, 30),
        location = "Stanford Humanities Center Board Room",
        status = "confirmed",
        description = """Adams Bodomo will.""",
        thumbnail = "https://picasaweb.google.com/104570033566114852437/201112SHCEvents#5659410196645602930",
        full_image = "https://picasaweb.google.com/104570033566114852437/201112SHCEvents#5659410456066390706")
    self.assertEquals(expected, description)
    
  def testParse(self):
    events = gcal.parse_feed("calendar.xml")
    expected = [gcal.Event(calendar_title = "Stanford Humanities Center Events", 
                            event_title = "Adams Bodomo: What is it like to be an African in China?",
                            event_id = "iir0l1284maac3f9c8rejr8f5c",
                            updated = "2011-09-29T17:58:43.000Z",
                            start_time = datetime.datetime(2011, 10, 13, 13, 30),
                            end_time = datetime.datetime(2011, 10, 13, 15, 30),
                            location = "Stanford Humanities Center Board Room",
                            status = "confirmed",
                            description = """Adams Bodomo will look at what has often been termed &quot;Africa&#39;s newest diaspora&quot; by reviewing contemporary Africa - China relations. Closer official interactions between these two areas have led to an increasing number of Africans visiting, settling, and forming communities in China. Bodomo will share the results of a study he undertook with 700 Africans across six main Chinese cities. The research addresses many aspects of everyday life of Africans in China, from why Africans go to China to how they are received by the Chinese state and certainly has theoretical implications for cross-cultural and cross-linguistic studies in an era of globalization.\n\nAdams Bodomo is African Studies Programme Director at the School of Humanities, University of Hong Kong. He obtained his PhD from the Norwegian University of Science and Technology after obtaining Bachelors and Masters Degrees at the University of Ghana.  Dr Bodomo has given invited lectures on the topic of Africans in China and on general Africa - China relations studies at several leading universities, including Yale University, SOAS, and Peking University. His latest book is entitled: &quot;Africans in China: An Investigation into the African Presence in China and its Consequences on Africa - China Relations&quot; (in press with Cambria Press, NY).""",
                            thumbnail = None, full_image = None)]
    self.assertEquals(expected[0], events[0])
  
  
if __name__ == '__main__':
  unittest.main()