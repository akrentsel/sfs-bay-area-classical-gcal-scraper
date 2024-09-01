import json
import os
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pytz
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the log level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format with timestamp, log level, and message
    handlers=[
        logging.FileHandler("daily_concert_sync.log"),  # Append logs to a file named 'daily_concert_sync.log'
        logging.StreamHandler()  # Also log to console
    ]
)


# SCOPES for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']

def load_concerts_from_directory(directory):
    """Load all concerts from JSON files in the specified directory."""
    concerts = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                concerts.extend(data)  # Add the contents of each file to the concerts list
    return concerts

def authenticate_google():
    """Authenticate the user and create a Google Calendar service."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build('calendar', 'v3', credentials=creds)
    return service

def get_or_create_calendar(service):
    """Get or create a Google Calendar for Bay Area Classical Concerts and return its ID."""
    calendar_summary = 'Bay Area Classical Concerts'

    # Check if the calendar already exists
    calendar_list = service.calendarList().list().execute()
    for calendar in calendar_list['items']:
        if calendar['summary'] == calendar_summary:
            logging.info(f"Found existing calendar: {calendar['id']}")
            return calendar['id']

    # If the calendar does not exist, create a new one
    calendar = {
        'summary': calendar_summary,
        'timeZone': 'America/Los_Angeles'  # Adjust timezone if needed
    }

    created_calendar = service.calendars().insert(body=calendar).execute()
    calendar_id = created_calendar['id']
    logging.info(f"Created new calendar with ID: {calendar_id}")
    return calendar_id

def make_calendar_public(service, calendar_id):
    """Make the Google Calendar public so it can be shared."""
    rule = {
        'role': 'reader',  # Public users will have read-only access
        'scope': {
            'type': 'default',  # 'default' scope makes it public
        }
    }

    service.acl().insert(calendarId=calendar_id, body=rule).execute()
    logging.info(f"Calendar with ID {calendar_id} is now public.")

def create_or_update_events(service, calendar_id, concerts):
    """Create or update Google Calendar events based on the concert data."""
    # Fetch existing events from Google Calendar
    events_result = service.events().list(calendarId=calendar_id).execute()
    existing_events = events_result.get('items', [])

    # Prepare a dictionary for quick lookup of existing events by title and date
    existing_events_dict = {
        (event['summary'], event['start'].get('dateTime')): event
        for event in existing_events
    }
    logging.info(f'Existing events: {existing_events_dict}')

    for concert in concerts:
        # Convert concert date and time to ISO format string
        if concert['date']:
            # Parse the datetime with timezone
            start_datetime = datetime.fromisoformat(concert['date'])
            end_datetime = (start_datetime + timedelta(hours=2)).isoformat()
        else:
            continue

        # Prepare event data
        event_data = {
            'summary': concert['title'],
            'description': concert['description'],
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'America/Los_Angeles',  # Adjust time zone if needed
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': 'America/Los_Angeles',
            },
            'location': concert['venue']
        }

        # Check if the event already exists
        event_key = (concert['title'], start_datetime.isoformat())
        logging.info(f'Searching for event key: {event_key}')
        if event_key in existing_events_dict:
            # Retrieve existing event details
            existing_event = existing_events_dict[event_key]
            existing_event_data = {
                'summary': existing_event.get('summary'),
                'description': existing_event.get('description'),
                'start': existing_event.get('start'),
                'end': existing_event.get('end'),
                'location': existing_event.get('location')
            }

            # Compare with new event data
            if existing_event_data == event_data:
                logging.info(f"No changes detected for event: {concert['title']} on {concert['date']}, skipping update.")
                continue  # Skip updating if no changes

            # Update the existing event if changes are detected
            event_id = existing_event['id']
            service.events().update(calendarId=calendar_id, eventId=event_id, body=event_data).execute()
            logging.info(f"Updated event: {concert['title']} on {concert['date']}")
        else:
            # Create a new event
            service.events().insert(calendarId=calendar_id, body=event_data).execute()
            logging.info(f"Created event: {concert['title']} on {concert['date']}")

def main():
    service = authenticate_google()
    # Get or create the calendar for SF Symphony Concerts
    calendar_id = get_or_create_calendar(service)
    # Make the new calendar public (only the first time)
    make_calendar_public(service, calendar_id)

    # Load concerts from all JSON files in the 'events' directory
    events_directory = 'events'
    concerts = load_concerts_from_directory(events_directory)

    # Create or update events in the new calendar
    create_or_update_events(service, calendar_id, concerts)

if __name__ == '__main__':
    main()
