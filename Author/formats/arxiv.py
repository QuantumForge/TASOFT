#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from operator import itemgetter
import sys

from .ta_auth import ta_auth

__author__    = 'William Hanlon'
__copyright__ = ''
__credits__   = ''
__license__   = ''
__version__   = '2.0.0'
__maintainer  = 'William Hanlon'
__email__     = 'whanlon@cosmic.utah.edu'
__status__    = 'Production'



class arxiv(ta_auth):
    def dumpAuthor(self):
        """Prints the TA author list in simple format for use on arXiv.org
        author lists."""

        self.sort_and_number_institutions()

        if self.outFileName is not None:
            origStdout = sys.stdout
            sys.stdout = open(self.outFileName, 'w')

        authnum = 1
        line = 'Telescope Array Collaboration: '
        for _, surname, initials, _, _, institution, _ in self.author_data:
            line += initials + ' ' + surname + ' ('

            inst_num = self.get_author_institution_numbers(institution)

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
        for key, value in sorted(self.institution_ordinal.items(), key =
                itemgetter(1)):
            line = line + '(' + str(value) + ') ' + key 
            if inst_count != len(self.institution_ordinal):
                line += ', '
            inst_count += 1
        line += ')'

        print(line)

        if self.outFileName is not None:
            sys.stdout.close()
            sys.stdout = origStdout

    def dump(self):
        self.dumpAuthor()

    def dumpFoot(self):
        pass

    def dumpAcknowledge(self):
        pass

