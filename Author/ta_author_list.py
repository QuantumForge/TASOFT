#!/usr/bin/env python
"""Prints out the TA authorlist using a formatted CSV file as input. The
columns of the file are expected to be:
    1. surname (last name)
    2. given name (full first name and middle name if desired)
    3. initials
    4. orcid
    5. institution short code (not used here)
    6. institution (delimited by {})
    7. status (only use so far is to designate someone as "deceased")

    an institution may actually consist of multiple institutions, with each
    individual institution contained in {}.

Multiple output formats are intended to be supported to alleviate the chance of
making mistakes when transcribing the author list to multiple TeX formats.

If attempting read the spreedsheet directly in the cloud using the google api,
the first attempt will require human intervention to grab credentials that
authorize you to read the sheet. See
https://developers.google.com/sheets/api/quickstart/python for an example on
how to do this."""

import argparse
import io
import os
import sys
import tempfile

from formats import ta_auth
from formats import aastex
from formats import plain_latex
from formats import authblk
from formats import arxiv

moduleLoaded = {}

# attempt to import google api modules
try:
    import httplib2
except ImportError:
    moduleLoaded['httplib2'] = False
else:
    moduleLoaded['httplib2'] = True

try:
    from apiclient import discovery
    from apiclient.http import MediaIoBaseDownload
except ImportError:
    moduleLoaded['apiclient'] = False
else:
    moduleLoaded['apiclient'] = True

try:
    from oauth2client import client
    from oauth2client import tools
    from oauth2client.file import Storage
except ImportError:
    moduleLoaded['oauth2client'] = False
else:
    moduleLoaded['oauth2client'] = True

SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
CLIENT_SECRET_FILE = 'client_secret_taauth.json'
APPLICATION_NAME = 'TA_AUTHOR_LIST'

def get_credentials(flags):
    """Gets valid credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
      Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
            'drive-python-taauthor.json')
    
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    # now if 'file' is empty assume the user wants to read the spreadsheet
    # directly from the cloud
    parser = argparse.ArgumentParser(parents=[tools.argparser],
            description='Sort the TA Author list in alphabetical order and '
            'affiliations in numerical order.\nIf file is not provided, '
            'attempt to read the master authorlist spreadsheet from the '
            'cloud.\n(Spreadsheet ID must be provided in a file named '
            '\'ta_author_list.txt\'.)')
    parser.add_argument('file', nargs = '?',
            help = 'TA Author list file name in CSV format')
    parser.add_argument('--format', choices=['plainLatex', 'plainText',
        'authblk', 'aastex', 'arxiv'], default='plainLatex',
        help='select the output format')
    parser.add_argument('--output', help='select the file to write to')
    parser.add_argument('--savecsv', action='store_true', default=False,
        help='save downloaded csv to ta_author.csv when reading from the cloud')

    args = parser.parse_args()

    if args.file is None:
        
        if (moduleLoaded['httplib2'] == False or
            moduleLoaded['apiclient'] == False or
            moduleLoaded['oauth2client'] == False):
            modMissing = ''
            for k, v in moduleLoaded.iteritems():
                if v == False:
                    modMissing += k + ' '

            sys.stderr.write('%s: Trying to read from the cloud, the following '
                'modules failed to load: %s\n' % (args.file, modMissing))
            sys.exit(1)

        credentials = get_credentials(args)
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('drive', 'v3', http=http)
        with open('ta_author_list.txt', 'r') as f:
            spreadsheetId = f.readline().strip()

        request = service.files().export_media(fileId=spreadsheetId,
                mimeType='text/csv')

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            #print "Download %d%%." % int(status.progress() * 100)


        if args.savecsv:
            csvfileName = 'ta_author.csv'
            csvfile = open(csvfileName, 'wb')
        else:
            csvfile = tempfile.NamedTemporaryFile(delete=False);
            csvfileName = csvfile.name
        with csvfile as f:
            f.write(fh.getvalue())
        fh.close()

    if args.file is None:
        inputCsvFile = csvfileName
    else:
        inputCsvFile = args.file

    if args.format == 'plainLatex':
        author_list = plain_latex.plain_latex()
    elif args.format == 'authblk':
        author_list = authblk.authblk()
    elif args.format == 'aastex':
        author_list = aastex.aastex()
    elif args.format == 'arxiv':
        author_list = arxiv.arxiv()
    else:
        author_list = ta_auth.ta_auth()

    author_list.read(inputCsvFile)
    author_list.dump(args.output)

    if args.file is None and args.savecsv == False:
        os.unlink(csvfileName)

if __name__ == '__main__':
    main()
