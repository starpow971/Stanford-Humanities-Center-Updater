#!/usr/bin/env python
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
data = """
{"apiVersion":"2.6",
 "data":{
   "kind":"calendar#eventFeed",
   "id":"http://www.google.com/calendar/feeds/stanford.humanities.events%40gmail.com/public/full",
   "author":{
     "displayName":"Stanford Humanities Events",
     "email":"stanford.humanities.events@gmail.com"
   },
   "title":"Stanford Humanities Center Events",
   "details":"Events sponsored and co-sponsored by the Stanford Humanities Center.",
   "updated":"2011-09-22T16:20:24.000Z",
   "totalResults":5,
   "startIndex":1,
   "itemsPerPage":25,
   "feedLink":"https://www.google.com/calendar/feeds/stanford.humanities.events%40gmail.com/public/full?v=2",
   "selfLink":"https://www.google.com/calendar/feeds/stanford.humanities.events%40gmail.com/public/full?alt=jsonc&max-results=25&showdeleted=true&v=2",
   "canPost":false,
   "timeZone":"America/Los_Angeles",
   "timesCleaned":0,
   "items":[
     {"kind":"calendar#event",
      "etag":"\"Ek4DRgJDeip7JGA6WhJW\"",
      "id":"kjms2bo60hci96v2isri11vl1g",
      "selfLink":"https://www.google.com/calendar/feeds/stanford.humanities.events%40gmail.com/public/full/kjms2bo60hci96v2isri11vl1g?v=2",
      "alternateLink":"https://www.google.com/calendar/event?eid=a2ptczJibzYwaGNpOTZ2MmlzcmkxMXZsMWcgc3RhbmZvcmQuaHVtYW5pdGllcy5ldmVudHNAbQ",
      "canEdit":false,
      "title":"Salon Featuring MK Raina",
      "created":"2011-09-13T22:17:25.000Z",
      "updated":"2011-09-22T16:20:24.000Z",
      "details":"SiCa-Humanites Center Arts writer/practitioner M.K. Raina", 
      "status":"confirmed",
      "creator":{"displayName":"stanford.humanities.events@gmail.com","email":"stanford.humanities.events@gmail.com"},
      "anyoneCanAddSelf":false,
      "guestsCanInviteOthers":true,
      "guestsCanModify":false,
      "guestsCanSeeGuests":true,
      "sequence":0,
      "transparency":"opaque",
      "location":"Stanford Humanities Center Board Room",
      "attendees":[{"rel":"organizer","displayName":"stanford.humanities.events@gmail.com","email":"stanford.humanities.events@gmail.com"}],
      "when":[{
          "start":"2011-10-11T16:00:00.000-07:00",
          "end":"2011-10-11T18:00:00.000-07:00"}]},
     {"kind":"calendar#event","etag":"\"Ek4IRQdIfip7JGA6WhJW\"","id":"iir0l1284maac3f9c8rejr8f5c","selfLink":"https://www.google.com/calendar/feeds/stanford.humanities.events%40gmail.com/public/full/iir0l1284maac3f9c8rejr8f5c?v=2","alternateLink":"https://www.google.com/calendar/event?eid=aWlyMGwxMjg0bWFhYzNmOWM4cmVqcjhmNWMgc3RhbmZvcmQuaHVtYW5pdGllcy5ldmVudHNAbQ","canEdit":false,"title":"Salon Featuring Adams Bodomo","created":"2011-09-21T21:04:54.000Z","updated":"2011-09-21T21:06:30.000Z","details":"","status":"confirmed","creator":{"displayName":"stanford.humanities.events@gmail.com","email":"stanford.humanities.events@gmail.com"},"anyoneCanAddSelf":false,"guestsCanInviteOthers":true,"guestsCanModify":false,"guestsCanSeeGuests":true,"sequence":0,"transparency":"opaque","location":"Stanford Humanities Center Board Room","attendees":[{"rel":"organizer","displayName":"stanford.humanities.events@gmail.com","email":"stanford.humanities.events@gmail.com"}],"when":[{"start":"2011-10-13T13:30:00.000-07:00","end":"2011-10-13T15:30:00.000-07:00"}]},{"kind":"calendar#event","etag":"\"Ek8JRARHeyp7JGA6WhJW\"","id":"lrqfu6fnfeft2lbfi0t49f50lk","selfLink":"https://www.google.com/calendar/feeds/stanford.humanities.events%40gmail.com/public/full/lrqfu6fnfeft2lbfi0t49f50lk?v=2","alternateLink":"https://www.google.com/calendar/event?eid=bHJxZnU2Zm5mZWZ0MmxiZmkwdDQ5ZjUwbGsgc3RhbmZvcmQuaHVtYW5pdGllcy5ldmVudHNAbQ","canEdit":false,"title":"Alastair Macaulay: \"Life, Art, Dance, and Criticism\"","created":"2011-09-20T17:41:45.000Z","updated":"2011-09-20T20:17:45.000Z","details":"Alastair Macaulay, chief dance critic of 'The New York Times' and former chief theatre critic for 'The Financial Times', has written in the past year about the movie 'Black Swan', about Grand Central Station as choreography, and about the artist Degas's depictions of ballet in painting and sculpture. He speaks about reviewing the performing arts today within a wider cultural framework.","status":"confirmed","creator":{"displayName":"stanford.humanities.events@gmail.com","email":"stanford.humanities.events@gmail.com"},"anyoneCanAddSelf":false,"guestsCanInviteOthers":true,"guestsCanModify":false,"guestsCanSeeGuests":true,"sequence":0,"transparency":"opaque","location":"Stanford Humanities Center Levinthal Hall","attendees":[{"rel":"organizer","displayName":"stanford.humanities.events@gmail.com","email":"stanford.humanities.events@gmail.com"}],"when":[{"start":"2011-11-02T16:00:00.000-07:00","end":"2011-11-02T18:00:00.000-07:00"}]},{"kind":"calendar#event","etag":"\"EEkKQgJIfCp7JGA6WhJW\"","id":"af5b02b4nrtdim7htnm4i76p7o","selfLink":"https://www.google.com/calendar/feeds/stanford.humanities.events%40gmail.com/public/full/af5b02b4nrtdim7htnm4i76p7o?v=2","alternateLink":"https://www.google.com/calendar/event?eid=YWY1YjAyYjRucnRkaW03aHRubTRpNzZwN28gc3RhbmZvcmQuaHVtYW5pdGllcy5ldmVudHNAbQ","canEdit":false,"title":"Brianne Bilsky (English, Ph.D. Candidate), on Teresa Hak Kyung Cha's \"Dict\0xE9e\"","created":"2011-08-30T16:41:19.000Z","updated":"2011-08-30T16:41:32.000Z","details":"Brianne Bilsky will lead a discussion on Theresa Hak Kyung Cha\0x2019s Dictee and the cultural politics of media theory. Dictee is a hybrid text constructed from an array of media forms including the printed word, calligraphically drawn Chinese characters, handwritten documents, typed letters, diagrams, film stills, and photographs. It also engages a variety of historical periods and subjects ranging from the 1910-1945 Japanese occupation of Korea and the development of Korean nationalism throughout the twentieth century to exile, oppression, and historiography. How does the way information is presented\0x2014printed word, photograph, handwritten document, etc.\0x2014relate to the aesthetic and cultural concerns that Dictee raises? What do these moments of media interaction reveal about the nature of historical narrative and information storage? We\0x2019ll use pre-distributed readings from Dictee and Brianne\0x2019s work on Cha\0x2019s text as a starting point for our discussion.","status":"canceled","creator":{"displayName":"Graphic Narrative Project"},"anyoneCanAddSelf":false,"guestsCanInviteOthers":true,"guestsCanModify":false,"guestsCanSeeGuests":true,"sequence":0,"transparency":"opaque","location":"Humanities Center Board Room","attendees":[{"rel":"organizer","displayName":"Graphic Narrative Project","email":"1o8jo65ni7npb02l2kfvi9sibg@group.calendar.google.com"}],"when":[{"start":"2011-10-19T18:00:00.000-07:00","end":"2011-10-19T20:00:00.000-07:00"}]},{"kind":"calendar#event","etag":"\"GUwITgBJfip7JGA6WhJX\"","id":"k3t8504gl02atkj45am9miajms","selfLink":"https://www.google.com/calendar/feeds/stanford.humanities.events%40gmail.com/public/full/k3t8504gl02atkj45am9miajms?v=2","alternateLink":"https://www.google.com/calendar/event?eid=azN0ODUwNGdsMDJhdGtqNDVhbTltaWFqbXMgc3RhbmZvcmQuaHVtYW5pdGllcy5ldmVudHNAbQ","canEdit":false,"title":"Test","created":"2011-08-15T22:11:20.000Z","updated":"2011-08-15T22:11:20.000Z","details":"","status":"confirmed","creator":{"displayName":"stanford.humanities.events@gmail.com","email":"stanford.humanities.events@gmail.com"},"anyoneCanAddSelf":false,"guestsCanInviteOthers":true,"guestsCanModify":false,"guestsCanSeeGuests":true,"sequence":0,"transparency":"opaque","location":"","attendees":[{"rel":"organizer","displayName":"stanford.humanities.events@gmail.com","email":"stanford.humanities.events@gmail.com"}],"when":[{"start":"2011-08-16T15:00:00.000-07:00","end":"2011-08-16T19:30:00.000-07:00"}]}]}}"""


class GcalTest(unittest.TestCase):
	def testParse(self):
		events = gcal.parseFeed(data)
		expected = [gcal.Event(calendar_title = "Stanford Humanities Center Events", 
														event_title = "Salon Featuring MK Raina",
														event_id = "kjms2bo60hci96v2isri11vl1g",
														start_time = datetime.datetime(2011, 10, 11, 16),
														end_time = datetime.datetime(2011, 10, 11, 18),
														location = "Stanford Humanities Center Board Room",
														status = "confirmed",
														description = "SiCa-Humanites Center Arts writer/practitioner M.K. Raina")]
		self.assertEquals(expected[0], events[0])
	
	
if __name__ == '__main__':
  unittest.main()