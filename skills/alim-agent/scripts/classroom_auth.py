#!/usr/bin/env python3
"""
Google Classroom OAuth setup for Alim agent.
Run this once to authenticate and store tokens.
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes needed for Classroom read/write
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.me',
    'https://www.googleapis.com/auth/classroom.coursework.students',
    'https://www.googleapis.com/auth/classroom.announcements.readonly',
    'https://www.googleapis.com/auth/classroom.materials.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
]

TOKEN_PATH = os.path.expanduser('~/.hermes/alim/google_token.json')
CREDENTIALS_PATH = os.path.expanduser('~/.hermes/alim/google_credentials.json')

def print_setup_instructions():
    """Print instructions for getting OAuth credentials."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║  Google Classroom OAuth Setup for Alim Agent                ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. Go to https://console.cloud.google.com/                  ║
║  2. Create a new project (or select existing)               ║
║  3. Enable APIs:                                             ║
║     - Google Classroom API                                   ║
║     - Google Drive API (for materials)                      ║
║  4. Create OAuth 2.0 credentials:                           ║
║     - Application type: Desktop app                         ║
║     - Download the JSON file                                ║
║  5. Save it as:                                              ║
║     ~/.hermes/alim/google_credentials.json                  ║
║                                                              ║
║  Alim will use these credentials to access your courses.    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

def setup():
    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)

    if not os.path.exists(CREDENTIALS_PATH):
        print_setup_instructions()
        print(f"ERROR: Credentials file not found at {CREDENTIALS_PATH}")
        return False

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
    creds = flow.run_local_server(port=0)

    with open(TOKEN_PATH, 'w') as token:
        token.write(creds.to_json())

    print(f"✓ Token saved to {TOKEN_PATH}")
    print("✓ Alim agent can now access your Google Classroom courses.")
    return True

def get_service():
    """Get an authenticated Classroom service."""
    if not os.path.exists(TOKEN_PATH):
        print("ERROR: Not authenticated. Run setup first.")
        return None

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    creds.refresh(Request())

    from googleapiclient.discovery import build
    service = build('classroom', 'v1', credentials=creds)
    return service

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'setup':
        setup()
    elif len(sys.argv) > 1 and sys.argv[1] == 'test':
        service = get_service()
        if service:
            courses = service.courses().list(pageSize=10).execute()
            for course in courses.get('courses', []):
                print(f"  {course['name']} ({course['id']})")
    else:
        print("Usage: python3 classroom_auth.py setup|test")
