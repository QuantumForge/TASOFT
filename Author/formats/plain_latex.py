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
__credits__   = 'Dmitri Ivanonv'
__license__   = ''
__version__   = '2.0.0'
__maintainer  = 'William Hanlon'
__email__     = 'whanlon@cosmic.utah.edu'
__status__    = 'Production'

class plain_latex(ta_auth):
    """Prints the author list in generic LaTeX format. No additional packages
    are required to use this format in a LaTeX document."""

    def dumpPreamble(self):
        if self.outFileName is not None:
            origStdout = sys.stdout
            sys.stdout = open(self.outFileName, 'w')

        print("""\\documentclass[10pt]{article}
\\usepackage[margin=1in]{geometry}

\\title{Telescope Array Collaboration}
\\date{}

\\begin{document}

\\maketitle
""")

        if self.outFileName is not None:
            sys.stdout.close()
            sys.stdout = origStdout

    def dumpAuthor(self):
    # generate a unique list of insitutions and their numbering as they
    #should appear in the author list
        self.sort_and_number_institutions()

        if self.outFileName is not None:
            origStdout = sys.stdout
            sys.stdout = open(self.outFileName, 'a')

        print("""\\makeatletter
\\newcommand{\\ssymbol}[1]{^{\\@fnsymbol{#1}}}
\\makeatother
\\par\\noindent""")

        # keep track of authors that have the status field filled. each
        # time we encounter a non-empty status field, we increment nstatus
        # and include a footnote with a different footnote symbol
        nstatus = 0
        status_data = []

        linenum = 1
        for _, surname, initials, _, _, institution, status in self.author_data:
            line = ''
            if linenum == len(self.author_data):
                line = 'and '
            # handle the case where the surname has a space in it,
            # i.e., di Matteo
            surname = surname.replace(' ', '~')
            line = line + initials + "~" + surname + '$^{'

            # get a sorted list of institution numbers for this author
            inst_num = self.get_author_institution_numbers(institution)

            i = 0
            # institution numbers are sorted
            for j in inst_num:
                if i > 0:
                    line += ','
                line += str(j)
                i += 1

            if status != '':
                nstatus += 1
                #line += '*'
                line += '\\ssymbol{{{0}}}'.format(nstatus)
                status_data.append(status)
            line += '}$'
            if linenum != len(self.author_data):
                line += ','
            print(line)
            linenum += 1

        print('\\bigskip')
        print('\\par\\noindent')
        print('{\\footnotesize\\it')

        for key, value in sorted(self.institution_ordinal.items(),
                key = itemgetter(1)):
            line = '$^{' + str(value) + '}$ ' + key + ' \\\\'
            print(line)

        print('')
        for i in range(len(status_data)):
            print('\\let\\thefootnote\\relax\\footnote{{$\\ssymbol{{{0}}}$ {1}}}'.format(i + 1, status_data[i]))
        print('\\addtocounter{footnote}{-1}\\let\\thefootnote\\svthefootnote')
        print('}')
        print('\\par\\noindent')

        if self.outFileName is not None:
            sys.stdout.close()
            sys.stdout = origStdout
