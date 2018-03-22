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
import os
import sys

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs = 1,
            help = 'pass the unsorted TA Author list file name')
    parser.add_argument('--format', choices=['plain', 'plainLatex', 'authblk',
        'aastex', 'arxiv'], default='plainLatex',
        help='select the output format')
    parser.add_argument('--output', help='select the file to write to')

    if len(sys.argv) == 1:
        sys.stdout.write("\n");
        sys.stdout.write("Sort the TA Author list in alphabetical order and affiliations in numerical order\n");
        sys.stdout.write("Up to 4 affiliations per author can be parsed.  If needed more affiliations then edit the script.\n");
        sys.stdout.write("Author: D. Ivanov <dmiivanov@gmail.com>\n\n");
        parser.print_help()
        sys.stdout.write("\n\n")
        sys.exit(1)

    args = parser.parse_args()

    if not os.access(args.files[0], os.R_OK):
        sys.stderr.write('%s: Can\'t read %s\n' %
                (os.path.basename(sys.argv[0]), args.files[0]))
        sys.exit(1)

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

    author_list.read(args.files[0])
    author_list.dump(args.output)

if __name__ == '__main__':
    main()
