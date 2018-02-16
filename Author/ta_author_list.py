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
making mistakes when transcribing the author list to multiple TeX formats."""

import argparse
import sys

from formats import aastex
from formats import plain_latex
from formats import authblk
from formats import arxiv

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

    if args.format == 'plainLatex':
        author_list = plain_latex.plain_latex()
    elif args.format == 'authblk':
        author_list = authblk.authblk()
    elif args.format == 'aastex':
        author_list = aastex.aastex()
    elif args.format == 'arxiv':
        author_list = arxiv.arxiv()
    else:
        author_list = ta_auth()

    author_list.read(args.files[0])
    author_list.dump()

if __name__ == '__main__':
    main()
