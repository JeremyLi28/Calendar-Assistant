from __future__ import print_function
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from dateutil.parser import parse
import sys

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'

def main():
    offset = 0
    if len(sys.argv) > 1:
	offset = int(sys.argv[1])
    print('=== Weekly Hour Summary ===')
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    # Get events for calendars
    today = datetime.now() + timedelta(days=offset * 7)
    weekstart = today - timedelta(days=today.weekday()) - timedelta(hours=today.hour) - timedelta(minutes=today.minute) - timedelta(seconds=today.second)
    weekend = weekstart + timedelta(days=7)

    print('Start: ' + str(weekstart), 'End: ' + str(weekend))
    
    calendars = ['primary', 'jeremyli@google.com', 'bf3ed2cg56hkll7alqgvu0e6dc@group.calendar.google.com']
    calendar_events = {}
    for id in calendars:
    	events_result = service.events().list(calendarId=id, timeMin=weekstart.isoformat() + 'Z',
                                        timeMax=weekend.isoformat() + 'Z', singleEvents=True, orderBy='startTime').execute()
    	calendar_events[id]  = events_result.get('items', [])

    total_sec = 0
    for calendar in calendar_events:
        print("== " + str(calendar) + " ==")
	print("Events:")
        calendar_sec = 0
    	for event in calendar_events[calendar]:
            start = event['start']['dateTime']
	    end = event['end']['dateTime']
	    summary = event['summary'] if 'summary' in event else 'No summary'
            duration = parse(end) - parse(start)
            duration_hour = duration.seconds / 3600
            duration_min = (duration.seconds % 3600) / 60
            print(start, end, summary, str(duration_hour) + 'h', str(duration_min) + 'm')
	    calendar_sec += duration.seconds
        print("Calendar hours: " + str(calendar_sec / 3600) + "h" + str((calendar_sec % 3600) / 60) + 'm')
        total_sec += calendar_sec
    print("*** Total hours: " + str(total_sec / 3600) + "h" + str((total_sec % 3600) / 60) + 'm ***')

if __name__ == '__main__':
    main()

