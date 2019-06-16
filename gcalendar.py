import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


class Event:
    def __init__(self, title: str, location: str, description: str, start: str, end: str):
        self.event = {
            'summary': title,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start,
                'timeZone': 'Europe/Amsterdam',
            },
            'end': {
                'dateTime': end,
                'timeZone': 'Europe/Amsterdam',
            },
            'reminders': {
                'useDefault': False,
            }
        }

    def get_event(self):
        return self.event


class Calendar:
    def __init__(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)

    def add_event(self, event: Event):
        self.service.events().insert(calendarId='primary', body=event.get_event()).execute()
