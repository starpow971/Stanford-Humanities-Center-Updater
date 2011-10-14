# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: interface with calendar server, parse calendar responses, 
# produce useful event objects.


from Cheetah.Template import Template

t = Template(file="calendar-landing-page.tmpl")

class CalendarTemplate(Template):
	calendar_title = 'STANFORD HUMANITIES CENTER EVENTS'
	event_title = 'Salon Featuring MK Raina'
	date = 'Tuesday, October 11, 2011'
	start_time = '4'
	end_time = '6 pm'
	location = 'Humanities Center Board Room'
	
t2 = CalendarTemplate(Template)

print t2