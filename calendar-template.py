# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: interface with calendar server, parse calendar responses, 
# produce useful event objects.


from Cheetah.Template import Template

templateDef = """
	<html>
	<head><title>Calendar</title></head>
	<body>
	<h1>Events Calendar</h1><br /><br /><h2>Upcoming Events</h2><br /><br />
	<span style="font-size:11px; ">$calendar_title</span><span style="font-size:13px; "><br />
	</span><span style="font-size:14px; color:#70694E;font-weight:bold; ">$event_title</span>
	<span style="font-size:13px; "><br />$date | $start_time-$end_time | $location<br /><br /><hr>
	<br /></span>
	</body>
	</html>"""

class CalendarTemplate(Template):
	calendar_title = 'STANFORD HUMANITIES CENTER EVENTS'
	event_title = 'Salon Featuring MK Raina'
	date = 'Tuesday, October 11, 2011'
	start_time = '4'
	end_time = '6 pm'
	location = 'Humanities Center Board Room'
	
t2 = CalendarTemplate(templateDef)

print t2