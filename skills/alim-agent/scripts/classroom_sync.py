#!/usr/bin/env python3
"""
Alim agent — Google Classroom sync.
Pulls course materials, assignments, and announcements into the knowledge base.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add venv to path for Google API client
sys.path.insert(0, '/data/.venv-alim/lib/python3.13/site-packages')

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.me',
    'https://www.googleapis.com/auth/classroom.coursework.students',
    'https://www.googleapis.com/auth/classroom.announcements.readonly',
    'https://www.googleapis.com/auth/classroom.materials.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
]

HOME = Path.home()
ALIM_DIR = HOME / '.hermes' / 'alim'
TOKEN_FILE = ALIM_DIR / 'google_token.json'
COURSES_FILE = ALIM_DIR / 'courses.json'

def get_service():
    if not TOKEN_FILE.exists():
        print("ERROR: Not authenticated. Run classroom_auth.py setup first.")
        return None
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    creds.refresh(Request())
    return build('classroom', 'v1', credentials=creds)

def list_courses(service):
    """List all active courses."""
    results = service.courses().list(pageSize=50).execute()
    courses = results.get('courses', [])
    for c in courses:
        print(f"  {c['name']} | ID: {c['id']} | {c.get('section', '')}")
    return courses

def sync_course(service, course_id, course_name):
    """Sync a single course's materials into the knowledge base."""
    safe_name = course_name.lower().replace(' ', '-').replace('/', '-')
    course_dir = ALIM_DIR / 'courses' / safe_name
    course_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== Syncing: {course_name} ===")

    # Get coursework
    try:
        cw = service.courses().coursework().list(courseId=course_id).execute()
        items = cw.get('coursework', [])
        print(f"  Coursework items: {len(items)}")

        for item in items:
            title = item.get('title', 'Untitled')
            work_type = item.get('workType', 'unknown')
            due_date = item.get('dueDate', {})
            due_str = f"{due_date.get('year', '')}-{due_date.get('month', ''):02d}-{due_date.get('day', ''):02d}" if due_date else 'no due date'
            description = item.get('description', '')[:200]

            print(f"  [{work_type}] {title} (due: {due_str})")

            # Save to knowledge base
            item_file = course_dir / 'assignments' / f"{title.lower().replace(' ', '-')}.md"
            item_file.parent.mkdir(parents=True, exist_ok=True)
            with open(item_file, 'w') as f:
                f.write(f"# {title}\n")
                f.write(f"- **Type**: {work_type}\n")
                f.write(f"- **Due**: {due_str}\n")
                f.write(f"- **Course**: {course_name}\n")
                f.write(f"- **Synced**: {datetime.now().isoformat()}\n\n")
                if description:
                    f.write(f"## Description\n{description}\n")
    except Exception as e:
        print(f"  Error syncing coursework: {e}")

    # Get announcements
    try:
        ann = service.courses().announcements().list(courseId=course_id).execute()
        announcements = ann.get('announcements', [])
        print(f"  Announcements: {len(announcements)}")

        ann_dir = course_dir / 'announcements'
        ann_dir.mkdir(parents=True, exist_ok=True)
        for a in announcements:
            text = a.get('text', '')[:500]
            created = a.get('creationTime', '')
            print(f"  - {created}: {text[:80]}...")
    except Exception as e:
        print(f"  Error syncing announcements: {e}")

    # Get course materials
    try:
        materials = service.courses().courseWorkMaterials().list(courseId=course_id).execute()
        mats = materials.get('courseWorkMaterial', [])
        print(f"  Materials: {len(mats)}")

        mat_dir = course_dir / 'materials'
        mat_dir.mkdir(parents=True, exist_ok=True)
        for m in mats:
            title = m.get('title', 'Untitled')
            desc = m.get('description', '')[:300]
            print(f"  - {title}")

            mat_file = mat_dir / f"{title.lower().replace(' ', '-')}.md"
            with open(mat_file, 'w') as f:
                f.write(f"# {title}\n")
                f.write(f"- **Course**: {course_name}\n")
                f.write(f"- **Synced**: {datetime.now().isoformat()}\n\n")
                if desc:
                    f.write(f"{desc}\n")
    except Exception as e:
        print(f"  Error syncing materials: {e}")

    print(f"  ✓ Synced to {course_dir}")

def sync_all():
    """Sync all courses."""
    service = get_service()
    if not service:
        return

    courses = list_courses(service)
    if not courses:
        print("No courses found.")
        return

    # Save course list
    ALIM_DIR.mkdir(parents=True, exist_ok=True)
    with open(COURSES_FILE, 'w') as f:
        json.dump([{'id': c['id'], 'name': c['name']} for c in courses], f, indent=2)

    for course in courses:
        sync_course(service, course['id'], course['name'])

    print(f"\n✓ All courses synced to {ALIM_DIR / 'courses'}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        service = get_service()
        if service:
            list_courses(service)
    elif len(sys.argv) > 1 and sys.argv[1] == 'sync':
        sync_all()
    else:
        print("Usage: python3 classroom_sync.py list|sync")
