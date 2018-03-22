#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = "William Hanlon"
__email__   = "whanlon@cosmic.utah.edu"
__version__ = "1.1.0"

from operator import itemgetter
import sys
from ta_auth import ta_auth

class arxiv(ta_auth):
    def dump(self, fileName = None):
        """Prints the TA author list in simple format for use on arXiv.org
        author lists."""

        inst_dict = self.sort_and_number_institutions()

        if fileName is not None:
            origStdout = sys.stdout
            sys.stdout = open(fileName, 'w')

        authnum = 1
        line = 'Telescope Array Collaboration: '
        for _, surname, initials, _, institution, _ in self.author_data:
            line += initials + ' ' + surname + ' ('

            inst_num = self.get_author_institution_numbers(institution, inst_dict)

            i = 0
            # institution numbers are sorted
            for j in inst_num:
                if i > 0:
                    line += ','
                line += str(j)
                i += 1

            line += ')'
            if authnum != len(self.author_data):
                line += ', '
            authnum += 1

        # now add the list of institutions
        inst_count = 1
        line += ' ('
        for key, value in sorted(inst_dict.items(), key = itemgetter(1)):
            line = line + '(' + str(value) + ') ' + key 
            if inst_count != len(inst_dict):
                line += ', '
            inst_count += 1
        line += ')'

        print line


        if fileName is not None:
            sys.stdout.close()
            sys.stdout = origStdout
