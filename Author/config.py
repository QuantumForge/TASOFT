#!/usr/bin/env python
"""store module and program configuration data in a central location."""

import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# if user wants to read the author spreadsheet from my google drive, the
# file pointed to by AUTHOR_ID_FILE must contain a single line with the
# spreadsheet id
AUTHOR_ID_FILE = os.path.join(ROOT_DIR, 'ta_author_id.txt')
# if user wants to read the acknowledgements doc from my google drive, the
# file pointed to by ACKNOWLEDGEMENTS_ID_FILE must contain a single line with
# the spreadsheet id
ACKNOWLEDGEMENTS_ID_FILE = os.path.join(ROOT_DIR, 'ta_acknowledgements_id.txt')
# define google api scope
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.readonly']
# location of authentication token
CLIENT_SECRET_FILE = os.path.join(ROOT_DIR, 'client_secret_taauth.json')
# google api application name
APPLICATION_NAME = 'TA_AUTHOR_LIST'
