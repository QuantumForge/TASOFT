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
__version__ = "1.0.0"

from operator import itemgetter
import re
from ta_auth import ta_auth

class authblk(ta_auth):
	"""Prints the author list in for use with the authblk package."""
    
	def dump(self):
		# generate a unique list of insitutions and their numbering as they
		# should appear in the author list
		inst_dict = self.sort_and_number_institutions()

		# give a hint as to what package to use and options we are using
		print '\\usepackage[affil-it]{authblk}'
		print '\\renewcommand\\Affilfont{\\itshape\\footnotesize}'

		for _, surname, initials, _, institution, status in self.author_data:
			line = '\\author['

			# get a sorted list of institution numbers for this author
			inst_num = self.get_author_institution_numbers(institution, inst_dict)

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
			print line

		for key, value in sorted(inst_dict.items(), key = itemgetter(1)):
			line = '\\affil[' + str(value) + ']{' + key + '}'
			print line
	
