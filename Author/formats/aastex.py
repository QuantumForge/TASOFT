#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This function takes an authorlist which is list of tuples with the following
values
1) sortKey
2) author surname
3) author initials
4) author orcid number
5) institutions
6) status
and produces the author list output formatted for AASTeX publications."""

import re
import sys

from .ta_auth import ta_auth

__author__    = 'William Hanlon'
__copyright__ = ''
__credits__   = ''
__license__   = ''
__version__   = '1.1.0'
__maintainer  = 'William Hanlon'
__email__     = 'whanlon@cosmic.utah.edu'
__status__    = 'Production'

class aastex(ta_auth):
    def dumpPreamble(self):
        if self.outFileName is not None:
            origStdout = sys.stdout
            sys.stdout = open(self.outFileName, 'w')

        print("""\\documentclass{aastex62}
\\begin{document}
\\title{Telescope Array Collaboration}
\\date{}
""")
        if self.outFileName is not None:
            sys.stdout.close()
            sys.stdout = origStdout

    def dumpAuthor(self):
        """Prints the author list for use with the aastex62 package."""

        if self.outFileName is not None:
            origStdout = sys.stdout
            sys.stdout = open(self.outFileName, 'a')

        for _, surname, initials, orcid, institution, status in \
                self.author_data:
            line = '\\author'
            if orcid != '':
                line += '[' + orcid + ']'
            line += '{' + initials + ' ' + surname + '}'
            print(line)

            if status != '':
                line = '\\altaffiliation{' + status + '}'
                print(line)

            # institutions this author belongs to
            for m in re.split('\} *\{', institution):
                inst = m.strip('{}')
                line = '\\affiliation{' + inst + '}'
                print(line)

            print('')

        if self.outFileName is not None:
            sys.stdout.close()
            sys.stdout = origStdout
