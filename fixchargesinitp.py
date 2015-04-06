#! /usr/bin/env python3.4

########################################################################
#                                                                      #
# This script is meant to take charges from a antechamber file (of     #
# somewhat specific formatting), and put them into an itp file         #
# generated by acpype.py. Specifically, the *GMX.itp file.             #
# This script was written by Thomas Heavey in 2015.                    #
#        theavey@bu.edu     thomasjheavey@gmail.com                    #
#                                                                      #
# Copyright 2015 Thomas J. Heavey IV                                   #      
#                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");      #
# you may not use this file except in compliance with the License.     #
# You may obtain a copy of the License at                              #
#                                                                      #
#    http://www.apache.org/licenses/LICENSE-2.0                        #
#                                                                      #
# Unless required by applicable law or agreed to in writing, software  #
# distributed under the License is distributed on an "AS IS" BASIS,    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or      #
# implied.                                                             #
# See the License for the specific language governing permissions and  #
# limitations under the License.                                       #
#                                                                      #
########################################################################


# This script takes two arguments. The first is the *resp.ac from which
# the charges will be taken.
# The second is the *GMX.itp file in which the charges need to be
# replaced. It will generate a backup file *GMX.itp.bak that is the
# original file without any edits.

# Note, this is not written to accomodate three character atom names
# so molecules with more than 100 atoms may cause issues as this is
# currently implemented. (shouldn't be hard to fix, though)

# This is written to work with python 3.4 because it should be good to
# be working on the newest version of python.

import fileinput  # allows easy iteration over a file
import sys        # For importing the arguments given
import re         # RegEx package for sorting data

# First argument is the file to take the charges from.
# Second argument is the file in which the charges need to be fixed.
charge_from = sys.argv[1]
charge_to   = sys.argv[2]
# An empty dictionary that will hold the names and charges.
charge_list = {} 

for line in fileinput.input(charge_from):
    if line.startswith('ATOM'):
        linelist = re.split(' {1,}',line)
        # print(linelist)
        charge_list.update({linelist[2]:linelist[8]})

print('{} charges taken from {}'.format(len(charge_list), charge_from))

# Initialize value of right_section (the top of the file is not the
# correct section to start editing).
right_section = False
# Initialize counter for changes made
lines_written = 0

for line in fileinput.input(charge_to, inplace=1, backup='.bak'):
    # Define boundaries of section I want to change:
    if line.startswith('[ atoms ]'):
        right_section = True
        sys.stdout.write(line)
        continue
    # at '[ bonds ]', should be done with all edits
    if line.startswith('[ bonds ]'):
        right_section = False
    if right_section:
        # ignore commented lines
        if line.startswith(';'):
            sys.stderr.write('skipping commented line\n')
            sys.stdout.write(line)
            continue
        # ignore blank lines
        if not line.rstrip():
            sys.stderr.write('skipping blank line\n')
            sys.stdout.write(line)
            continue
        #sys.stderr.write(str(line))
        try:
            # Read atom name from this line
            atom_name   = line[26:29]
            # Get atom's proper charge from the dict made above.
            # This is made a string of len 9 (which is the same len
            # as what it will be replacing).
            charge      = format(charge_list[atom_name],'>9')
        # Some atom names are only 2 characters, so, the space in the
        # atom name would not be properly recognized by the dict.
        # If a key is not recognized, it will attempt to take off the
        # first character of the atom name (probably a space) and try
        # again.
        except(KeyError):
            sys.stderr.write('Checking for two character atom name. KeyError was')
            sys.stderr.write(' raised. atom_name was "{}"\n'.format(atom_name))
            charge      = format(charge_list[atom_name[1:]],'>9')
        # Create new_line from parts the current charge with the correct charge.
        new_line = "".join([line[0:38], charge, line[47:]])
        # Print the line back to the file.
        sys.stdout.write(new_line)
        lines_written += 1
    else:
        sys.stdout.write(line)
fileinput.close()

print('{} lines replaced in file {}'.format(lines_written, charge_to))
