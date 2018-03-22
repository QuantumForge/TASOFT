#!/usr/bin/env python
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

__author__  = "William Hanlon"
__email__   = "whanlon@cosmic.utah.edu"
__version__ = "1.1.0"

import re
import sys
from ta_auth import ta_auth

class aastex(ta_auth):

    def dump(self, fileName = None):
        """Prints the author list for use with the aastex62 package."""

        if fileName is not None:
            origStdout = sys.stdout
            sys.stdout = open(fileName, 'w')

        for _, surname, initials, orcid, institution, status in \
                self.author_data:
            line = '\\author'
            if orcid != '':
                line += '[' + orcid + ']'
            line += '{' + initials + ' ' + surname + '}'
            print line

            if status != '':
                line = '\\altaffiliation{' + status + '}'
                print line

            # institutions this author belongs to
            for m in re.split('\} *\{', institution):
                inst = m.strip('{}')
                line = '\\affiliation{' + inst + '}'
                print line

            print ''

        if fileName is not None:
            sys.stdout.close()
            sys.stdout = origStdout
