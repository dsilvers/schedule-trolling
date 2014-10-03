#!/usr/bin/python

from config import *

import urllib2
import csv
import StringIO
import re
import datetime
import time

resources = {}
reservations = []
aircraft_count = 0
instructor_count = 0

""" Process Resources, separate into Aircraft and Instructors """
resources_raw = urllib2.urlopen(RESOURCE_URL).read()
csvreader = csv.reader(StringIO.StringIO(resources_raw))
row_no = 1
for resource_row in csvreader:
    if row_no > 1 and len(resource_row) > 2:
        if re.search(r"\$\d+", resource_row[1]):
            is_aircraft = True
        else:
            is_aircraft = False

        # long name, short name, is an aircraft
        resources[resource_row[0]] = [resource_row[1].strip(), resource_row[2].strip(), is_aircraft]
    
    row_no = row_no + 1

#for id in resources:
#    print id, resources[id][0], resources[id][1], resources[id][2] 
#print " - - - - - - - - - "

""" Process reservations """
reservations_raw = urllib2.urlopen(USER_URL).read()
resreader = csv.reader(StringIO.StringIO(reservations_raw))
row_no = 1
for resource_row in resreader:
    if row_no > 1 and len(resource_row) > 2:
        resource_id = str(resource_row[1]).strip()
        start_time = int(resource_row[2])
        end_time = int(resource_row[3])
        comment = resource_row[7]
        print start_time, int(time.time())
        if start_time > int(time.time()):
            try:
                if resources[resource_id][2]:
                    aircraft_count = aircraft_count + 1
                else:
                    instructor_count = instructor_count + 1
                reservations.append([resource_id, start_time, end_time, comment])
            except KeyError:
                print "Resource #" + str(resource_id) + " not found."
        else:
            print "Old reservation found"
    row_no = row_no + 1

#for reservation in reservations:
#    print reservation


""" Trolling time """
today = datetime.date.today()
subject = "Automated aircraft schedule trolling report for " + today.isoformat()
if instructor_count > 0 or aircraft_count > 0:
    subject = subject + " (" + str(instructor_count) + "/" + str(aircraft_count) + ")"
    message = "Automated trolling report for " + PERSON + ".\n\n" + PERSON + " has lessons scheduled.\n\n"

    for reservation in reservations:
        start = datetime.datetime.fromtimestamp(int(reservation[1])).strftime('%Y-%m-%d %H:%M')
        end = datetime.datetime.fromtimestamp(int(reservation[2])).strftime('%H:%M')
        message = message + start + " to " + end + " - " + resources[reservation[0]][1] + "  (" + reservation[3] + ")\n"
else:
    subject = subject + " - NO LESSONS SCHEDULED!"
    message = "Trollbot found NO GODDAMN LESSONS SCHEDULED. SCHEDULE SOME LESSONS!\n\n"


message = message + "\n\n" + str(instructor_count) + " instructor reservations\n" + str(aircraft_count) + " aircraft reservations\n\n\n\n\n\nReminder: The scheduler allows for you to schedule up to 6 aircraft and instructor sessions in advance. Do it."



from send_email import send_email
send_email(EMAIL_SENDER, EMAIL_TO, subject, message)

print message


