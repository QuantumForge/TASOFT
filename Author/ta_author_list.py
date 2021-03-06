#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Prints out the TA authorlist and acknowledgements using a
formatted CSV file of authors and a plain text file (containing LaTeX
formated text) as input. The columns of the author csv file are expected to be:
    1. surname (last name)
    2. given name (full first name and middle name if desired)
    3. initials
    4. orcid
    5. institution short code (not used here)
    6. institution (delimited by {})
    7. status (i.e., "deceased", "not at XYZ University") (appears as a
       footnote)

    an institution may actually consist of multiple institutions, with each
    individual institution contained in {}.

Multiple output formats are intended to be supported to alleviate the chance of
making mistakes when transcribing the author list to multiple TeX formats.

If attempting to read the spreedsheet directly in the cloud using the google
api, the first attempt will require human intervention to grab credentials that
authorize you to read the sheet. See
https://developers.google.com/sheets/api/quickstart/python for an example on how
to do this.

The CSV author spreadsheet ID and the plain text acknowledgements ID of the
documents storage on Google Drive are not stored in the source code. They 
are read from ta_author_id.txt and ta_acknowledgements_id.txt. Contact me
for the IDs if you wish to read from the cloud. Cloud access is not needed
to run this program. One can always go directly to the spreadsheet and doc,
export to your local drive as CSV and text files,
then provide those files as input using --csvfile and --ackfile.
"""

import argparse
import io
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil
import subprocess
import sys
import tempfile

from formats import ta_auth
from formats import aastex
from formats import plain_latex
from formats import authblk
from formats import arxiv
from formats import revtex

from config import AUTHOR_ID_FILE
from config import ACKNOWLEDGEMENTS_ID_FILE
from config import SCOPES
from config import CLIENT_SECRET_FILE
from config import APPLICATION_NAME

__author__    = 'William Hanlon'
__copyright__ = ''
__credits__   = ''
__license__   = ''
__version__   = '2.0.0'
__maintainer  = 'William Hanlon'
__email__     = 'whanlon@cosmic.utah.edu'
__status__    = 'Production'

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

#SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
#CLIENT_SECRET_FILE = 'client_secret_taauth.json'
#APPLICATION_NAME = 'TA_AUTHOR_LIST'

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

def getCloudData(args, docID, mimeType, outFileName):
    """User provides the Google Drive document ID,
    mime file type describing how the data is to be exported from Drive,
    and output file name to where it is locally exported to.

    if outFileName is None, then a temporary file is generated and user
    should destroy the file when they are done with it.
    
    This function returns the name of the output file."""

    if (moduleLoaded['httplib2'] == False or
        moduleLoaded['apiclient'] == False or
        moduleLoaded['oauth2client'] == False):
        modMissing = ''
        for k, v in moduleLoaded.items():
            if v == False:
                modMissing += k + ' '

        sys.stderr.write('%s: Trying to read from the cloud, the following '
            'modules failed to load: %s\n' % (args.csvfile, modMissing))
        sys.exit(1)

    credentials = get_credentials(args)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    request = service.files().export_media(fileId=docID,
            mimeType=mimeType)

    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        #print "Download %d%%." % int(status.progress() * 100)

    # if the user wants to save a copy of the author list that
    # was grabbed from the cloud store in in ta_author.csv
    # otherwise we use a temp file that is deleted when the
    # program exits
    if outFileName is None:
        outFile = tempfile.NamedTemporaryFile(delete=False)
        outFileName = outFile.name
    else:
        try:
            outFile = open(outFileName, 'wb')
        except:
            sys.stderr.write('Can\'t open %s.\n' % (outFileName))
            sys.exit(1)

    # dump the cloud document to a local file
    #with outFile as f:
        #z = fh.getvalue().decode('utf-8')
        #print('fh.getvalue(): ', z)
        #print(type(z))
        #f.write(fh.getvalue().decode('utf-8'))
    with io.open(outFileName, 'w', encoding='utf-8') as f:
        f.write(fh.getvalue().decode('utf-8'))
    fh.close()

    return outFileName

def makePDF(inputCsvFileName, inputAckFileName, pdfFileName):
    """Make a PDF file that contains the author list and acknowledgements."""
    pdfAbsPath = os.path.abspath(pdfFileName)
    ocwd = os.getcwd()
    tempDir = tempfile.mkdtemp()
    tempFileName = os.path.join(tempDir, 'ta_auth_temp.tex')

    author_list = authblk.authblk(inputCsvFileName, inputAckFileName,
            tempFileName)

    if inputCsvFileName is not None:
        author_list.readAuthor()

    author_list.dumpPreamble()

    if inputCsvFileName is not None:
        author_list.dumpAuthor()

    if inputAckFileName is not None:
        author_list.dumpAcknowledge()

    author_list.dumpFoot()

    os.chdir(tempDir)
    subprocess.call(['pdflatex', 'ta_auth_temp.tex'])
    shutil.move('ta_auth_temp.pdf', pdfAbsPath)
    os.chdir(ocwd)
    shutil.rmtree(tempDir)

def main():
    # now if 'csvfile' or 'ackfile' is empty assume the user wants to
    # read the spreadsheet directly from the cloud
    parser = argparse.ArgumentParser(parents=[tools.argparser],
            description='Sort the TA Author list in alphabetical order and '
            'affiliations in numerical '
            'order and output a working LaTeX skeleton file. If file is '
            'not provided, '
            'attempt to read the master authorlist spreadsheet from the '
            'cloud. (For reading from the cloud author spreadsheet ID '
            'must be provided in a file named \'ta_author_id.txt\' '
            'and acknowledgements doc ID must be provided in a file named '
            'ta_acknowledgements_id.txt.)')
    parser.add_argument('--csvfile',
            help = 'TA Author list input file name in CSV format')
    parser.add_argument('--ackfile',
            help = 'TA acknowledgements input file name in plain text format')
    parser.add_argument('--format', choices=['plainLatex', 'plainText',
        'authblk', 'aastex', 'arxiv', 'revtex'], default='plainLatex',
        help='select the output format')
    parser.add_argument('--stub-only', help='do not try to create a full '
            'LaTeX document, only output the relevant parts (author and/or '
            'acknowledgements)', default=False, action='store_true')
    parser.add_argument('--stats', help='dump counts of institutions and '
            'generate plot', action='store_true', default=False)
    parser.add_argument('--output', help='select the file to write to. '
            'if not provided, output is directed to STDOUT')
    parser.add_argument('--pdf', help='generate a PDF version of the '
            'authorlist and acknowledgements from the authblk template.')
    parser.add_argument('--include-ack', help='include acknowledments in '
            'output latex and pdf.', default=False, action='store_true')
    parser.add_argument('--ack-only', help='only include acknowledments in '
            'output latex and pdf (authors are removed).', default=False,
            action='store_true')
    parser.add_argument('--savecsv', action='store_true', default=False,
        help='save downloaded csv to ta_author.csv when reading from the cloud')
    parser.add_argument('--saveack', action='store_true', default=False,
        help='save downloaded acknowledgements to ta_acknowledgements.txt when '
        'reading from the cloud')

    args = parser.parse_args()

    # if no file on the command line is given, try to read from my
    # Google Drive
    if args.csvfile is None:
        # get the spreadsheet id from a local file
        try:
            with open(AUTHOR_ID_FILE, 'r') as f:
                docID = f.readline().strip()
        except:
            print('Can\'t read ', AUTHOR_ID_FILE, file=sys.stderr)
            sys.exit(1)
        if args.savecsv:
            saveFileName = 'ta_author.csv'
        else:
            saveFileName = None
        inputCsvFile = getCloudData(args, docID, 'text/csv', saveFileName)
    else:
        inputCsvFile = args.csvfile

    if args.ackfile is None:
        # get the spreadsheet id from a local file
        try:
            with open(ACKNOWLEDGEMENTS_ID_FILE, 'r') as f:
                docID = f.readline().strip()
        except:
            print('Can\'t read ', ACKNOWLEDGEMENTS_ID_FILE, file=sys.stderr)
            sys.exit(1)
        if args.saveack:
            saveFileName = 'ta_acknowledgements.txt'
        else:
            saveFileName = None
        # there's a lurking issue that docs exports the plain/text file as
        # utf-8 with a bom as the first byte.
        inputAckFile = getCloudData(args, docID, 'text/plain', saveFileName)
        # strip the BOM
        s = open(inputAckFile, mode='r', encoding='utf-8-sig').read()
        open(inputAckFile, mode='w', encoding='utf-8').write(s)
    else:
        inputAckFile = args.ackfile

    # invoke the template that produces the output based on what LaTeX
    # style the used requested.
    #
    # if args.output is None, then it prints the output to stdout.
    if args.format == 'plainLatex':
        author_list = plain_latex.plain_latex(inputCsvFile, inputAckFile,
                args.output)
    elif args.format == 'authblk':
        author_list = authblk.authblk(inputCsvFile, inputAckFile, args.output)
    elif args.format == 'aastex':
        author_list = aastex.aastex(inputCsvFile, inputAckFile, args.output)
    elif args.format == 'arxiv':
        author_list = arxiv.arxiv(inputCsvFile, inputAckFile, args.output)
    elif args.format == 'revtex':
        author_list = revtex.revtex(inputCsvFile, inputAckFile, args.output)
    else:
        author_list = ta_auth.ta_auth(inputCsvFile, inputAckFile, args.output)

    # readAuthor reads in the author CSV file and processes it quite a bit
    # to alphabetize and number institutions in order as they appear in the
    # author list.
    author_list.readAuthor()
    # there is no readAcknowledgements because we'll just dump the simple
    # contents of the file pointed to by inputAckFile to args.output

    # set the flag defaults. argparse is designed for easy toggling of multiple
    # booleans at the same time.
    author_flag = True
    ack_flag = False
    if args.include_ack:
        ack_flag = True
    if args.ack_only:
        author_flag = False
        ack_flag = True

    if author_flag and ack_flag:
        author_list.dump()
    elif author_flag and not ack_flag:
        if not args.stub_only:
            author_list.dumpPreamble()
        author_list.dumpAuthor()
        if not args.stub_only:
            author_list.dumpFoot()
    elif not author_flag and ack_flag:
        if not args.stub_only:
            author_list.dumpPreamble()
        author_list.dumpAcknowledge()
        if not args.stub_only:
            author_list.dumpFoot()

    if args.pdf:
        if author_flag and ack_flag:
            makePDF(inputCsvFile, inputAckFile, args.pdf)
        elif author_flag and not ack_flag:
            makePDF(inputCsvFile, None, args.pdf)
        elif not author_flag and ack_flag:
            makePDF(None, inputAckFile, args.pdf)

    if (args.stats):
        print('')
        author_list.stats_by_institution()
        c = author_list.institution_counter
        # sort institutions by number of authors
        sorted_c = c.most_common();
        bar_ind = np.arange(len(c))
        #bar_x = c.keys()
        #bar_y = c.values()
        bar_x = list(zip(*sorted_c))[0]
        bar_y = list(zip(*sorted_c))[1]
        width = 0.95

        fig = plt.figure(figsize=(15, 9))
        ax = fig.add_subplot(111)
        ax.bar(bar_ind, bar_y, width=width)
        ax.set_xticks(bar_ind)
        ax.set_xticklabels(bar_x, rotation=45, rotation_mode='anchor',
                ha='right')
        ax.set_title('TA Authors by Institution')
        ax.set_xlabel('Institution')
        ax.set_ylabel('Number of Authors')
        plt.show()


    if args.csvfile is None and args.savecsv == False:
        os.unlink(inputCsvFile)
    if args.ackfile is None and args.saveack == False:
        os.unlink(inputAckFile)


if __name__ == '__main__':
    main()
