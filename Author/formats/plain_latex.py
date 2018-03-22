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
and produces the author list output formatted for plain LaTeX."""

__author__  = "William Hanlon"
__email__   = "whanlon@cosmic.utah.edu"
__version__ = "1.1.0"

from operator import itemgetter
import re
import sys
from ta_auth import ta_auth

class plain_latex(ta_auth):
    """Prints the author list in generic LaTeX format. No additional packages
    are required to use this format in a LaTeX document."""

    def dump(self, fileName = None):
    # generate a unique list of insitutions and their numbering as they
    #should appear in the author list
        inst_dict = self.sort_and_number_institutions()

        if fileName is not None:
            origStdout = sys.stdout
            sys.stdout = open(fileName, 'w')

        print '\\par\\noindent'

        linenum = 1
        for _, surname, initials, _, institution, status in self.author_data:
            line = ''
            if linenum == len(self.author_data):
                line = 'and '
            # handle the case where the surname has a space in it,
            # i.e., di Matteo
            surname = surname.replace(' ', '~')
            line = line + initials + "~" + surname + '$^{'

            # get a sorted list of institution numbers for this author
            inst_num = self.get_author_institution_numbers(institution, inst_dict)

            i = 0
            # institution numbers are sorted
            for j in inst_num:
                if i > 0:
                    line += ','
                line += str(j)
                i += 1
            # at the moment status only applies to one person and that status is
            # "deceased". and only a "*" is assigned in the author list. if 
            # more statuses are needed, then this bit of code needs to change
            # and the status symbol will have to be selected as well on a
            # case-by-case basis or added as an additional field in the
            # author_data source
            if status != '':
                line += '*'
            line += '}$'
            if linenum != len(self.author_data):
                line += ','
            print line
            linenum += 1

        print '\\par\\noindent'
        print '{\\footnotesize\\it'

        for key, value in sorted(inst_dict.items(), key = itemgetter(1)):
            line = '$^{' + str(value) + '}$ ' + key + ' \\\\'
            print line

        print ''
        print '\\let\\thefootnote\\relax\\footnote{$^{*}$ Deceased}'
        print '\\addtocounter{footnote}{-1}\\let\\thefootnote\\svthefootnote'
        print '}'
        print '\\par\\noindent'

        if fileName is not None:
            sys.stdout.close()
            sys.stdout = origStdout
