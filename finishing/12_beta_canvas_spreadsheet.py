#!/bin/env python3
# -*- coding: utf-8; -*-
#
# Copyright (C) 2018 Colin B. Macdonald <cbm@m.fsf.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import csv

import importlib
myhash = importlib.import_module('11_prepare_coded_return').myhash

canvas_fromfile = 'canvas_from_export.csv'
canvas_tofile = 'canvas_for_import.csv'

# TODO: check if former exists and latter does not, and give some
# basic instructions


print('Walking "{0}" to generate return codes'.format(canvas_fromfile))
sns = {}
with open(canvas_fromfile, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')

    with open(canvas_tofile, 'w') as csvout:
        writer = csv.writer(csvout, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for i, row in enumerate(reader):
            if i == 0:
                assert row[0] == 'Student'
                # find index of the student number
                rsn = row.index('SIS User ID')
                # find the "return code (#####)" column
                # TODO: use regexp
                tmp = [i for i in range(len(row)) if 'return code (' in row[i].lower()]
                rcode, = tmp
            elif i == 1 or i == 2:
                # two lines of junk
                assert row[0] == '' or 'Points Possible' in row[0]
            else:
                name = row[0]
                sn = row[rsn]
                dorow = True
                if name == 'Test Student':
                    dorow = False
                assert len(name) > 0
                assert len(sn) == 8
                if dorow:
                    code = myhash(sn)
                    row[rcode] = code
                    sns[sn] = code
                    print('  row {0}, adding code {3} for {2} "{1}"'.format( \
                        i, name, sn, row[rcode]))
            writer.writerow(row)
print('File for upload to Canvas: "{0}"'.format(canvas_tofile))


print('Checking that each codedReturn paper has a corresponding student in the canvas sheet...')
for file in os.scandir('codedReturn'):
    filename = os.fsdecode(file)
    if filename.endswith(".pdf"):
        # TODO: this looks rather fragile!
        parts = filename.partition('_')[2].partition('.')[0]
        sn, meh, code = parts.partition('_')
        if sns[sn] == code:
            print('  Good: paper {2} has entry in the spreadsheet {0}, {1}'.format(
                sn, code, filename))
            sns.pop(sn)
        else:
            print('  Bad: we found a pdf file that has no student in the spreadsheet')
            print('    Filename: {0}'.format(filename))
            sys.exit()


# anyone that has a pdf file has been popped from the dict, report the remainders
if len(sns) == 0:
    print('Everyone listed in the canvas file has a pdf file')
else:
    print('The following people are in the spreadsheet but do not have a pdf file; did they write?')
    for (i, sn) in enumerate(sns):
        # TODO: name rank and serial number would be good
        print('  SN: {0}, code: {1}'.format(i,sn))
