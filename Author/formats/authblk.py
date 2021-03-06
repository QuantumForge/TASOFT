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
and produces the author list output formatted for plain LaTeX."""

from operator import itemgetter
import re
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


class authblk(ta_auth):
    """Prints the author list in for use with the authblk package."""

    def dumpPreamble(self):
        if self.outFileName is not None:
            origStdout = sys.stdout
            sys.stdout = open(self.outFileName, 'w')

        print("""\\documentclass[10pt]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[affil-it]{authblk}
\\usepackage[margin=1in]{geometry}
\\renewcommand\\Affilfont{\\itshape\\footnotesize}
\\DeclareUnicodeCharacter{FEFF}{}

\\title{Telescope Array Collaboration}

\\date{}

\\begin{document}

""")

        if self.outFileName is not None:
            sys.stdout.close()
            sys.stdout = origStdout

    def dumpAuthor(self):
        # generate a unique list of insitutions and their numbering as they
        # should appear in the author list
        self.sort_and_number_institutions()

        if self.outFileName is not None:
            origStdout = sys.stdout
            sys.stdout = open(self.outFileName, 'a')

        # give a hint as to what package to use and options we are using
        #print '\\usepackage[affil-it]{authblk}'
        #print '\\renewcommand\\Affilfont{\\itshape\\footnotesize}'

        for _, surname, initials, _, _, institution, status in self.author_data:
            line = '\\author['

            # get a sorted list of institution numbers for this author
            inst_num = self.get_author_institution_numbers(institution)

            i = 0
            for j in inst_num:
                if i > 0:
                    line += ','
                line += str(j)
                i += 1
            line += ']{' + initials + '~' + surname
            if status != '':
                line += '\\footnote{' + status + '}'
            line += '}'
            print(line)

        for key, value in sorted(self.institution_ordinal.items(), key =
                itemgetter(1)):
            line = '\\affil[' + str(value) + ']{' + key + '}'
            print(line)

        print('\\maketitle')
        print('')

        if self.outFileName is not None:
            sys.stdout.close()
            sys.stdout = origStdout

