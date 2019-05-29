#!/usr/bin/env python3
# -*- coding: utf-8; -*-
#
# Copyright (C) 2018-2019 Colin B. Macdonald <cbm@m.fsf.org>
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

import os, sys
import csv
from io import StringIO
import pandas

import utils
from utils import myhash


def import_canvas_csv(canvas_fromfile):
    # TODO: we strip the "Possible points" and muting: is this ok?
    df = pandas.read_csv(canvas_fromfile, skiprows=[1, 2])
    print('Loading from Canvas csv file: "{0}"'.format(canvas_fromfile))

    # TODO: talk to @andrewr about "SIS User ID" versus "Student Number"
    cols = ['Student', 'ID', 'SIS User ID', 'SIS Login ID', 'Section', 'Student Number']
    assert all([c in df.columns for c in cols]), "CSV file missing columns?  We need:\n  " + str(cols)

    print('Filtering out those named "Test Student" and w/o Student Numbers')
    isbad = df.apply(lambda x: x['Student'].lower().startswith('test student')
                             and pandas.isnull(x['Student Number']),
                     axis=1)
    df = df[isbad == False]
    # then force some integer columns
    df['Student Number'] = df['Student Number'].astype('int64')
    df['SIS User ID'] = df['SIS User ID'].astype('int64')
    # TODO: what if someone has non integer sections?  Better to "leave it alone"
    # But how?  It becomes float b/c of "Test Student"
    df['Section'] = df['Section'].astype('int64')
    return df


def find_partial_column_name(df, parthead, atStart=True):
    parthead = parthead.lower()
    if atStart:
        print('Searching for column starting with "{0}":'.format(parthead))
        possible_matches = [s for s in df.columns if s.lower().startswith(parthead)]
    else:
        print('Searching for column containing "{0}":'.format(parthead))
        possible_matches = [s for s in df.columns if s.lower().find(parthead) >= 0]
    print('  We found: ' + str(possible_matches))
    try:
        col, = possible_matches
    except ValueError as e:
        print('  Unfortunately we could not a find a unique column match!')
        raise(e)
    return col


def make_canvas_gradefile(canvas_fromfile, canvas_tofile, test_parthead='Test'):
    df = import_canvas_csv(canvas_fromfile)

    cols = ['Student', 'ID', 'SIS User ID', 'SIS Login ID', 'Section', 'Student Number']

    testheader = find_partial_column_name(df, test_parthead)
    cols.append(testheader)

    print('Extracting the following columns:\n  ' + str(cols))
    df = df[cols]

    if not all(df[testheader].isnull()):
        print('\n*** WARNING *** Target column "{0}" is not empty!\n'.format(testheader))
        print(df[testheader])
        input('Press Enter to continue and overwrite...')

    print('Loading "testMarks.csv" data')
    # TODO: should we be doing all this whereever testMarks.csv is created?
    marks = pandas.read_csv('testMarks.csv', sep='\t')

    # Make dict: this looks fragile, try merge instead...
    #marks = marks[['StudentID', 'Total']].set_index("StudentID").to_dict()
    #marks = marks['Total']
    #df['Student Number'] = df['Student Number'].map(int)
    #df[testheader] = df['Student Number'].map(marks)

    print('Performing "Left Merge"')
    df = pandas.merge(df, marks, how='left',
                      left_on='Student Number', right_on='StudentID')
    df[testheader] = df['Total']
    df = df[cols]  # discard again (e.g., PG specific stuff)

    print('Writing grade data "{0}"'.format(canvas_tofile))
    # index=False: don't write integer index for each line
    df.to_csv(canvas_tofile, index=False)
    return df


def canvas_csv_add_return_codes(canvas_fromfile, canvas_tofile):
    print('Walking "{0}" to generate return codes'.format(canvas_fromfile))
    with open(canvas_fromfile, 'r') as csvin:
        with open(canvas_tofile, 'w') as csvout:
            sns = _canvas_csv_add_return_codes(csvin, csvout)
    print('File for upload to Canvas: "{0}"'.format(canvas_tofile))
    return sns


def _canvas_csv_add_return_codes(csvin, csvout):
    reader = csv.reader(csvin, delimiter=',')
    writer = csv.writer(csvout, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    sns = {}
    for i, row in enumerate(reader):
        if i == 0:
            assert row[0] == 'Student', "First row should start with 'Student'"
            # find index of the student number
            rsn = row.index('SIS User ID')
            # find the "return code (#####)" column
            # TODO: use regexp
            tmp = [i for i in range(len(row)) if 'return code (' in row[i].lower()]
            assert tmp, 'Cannot find "return code" column'
            rcode, = tmp
        elif i == 1 or i == 2:
            # two lines of junk
            assert row[0] == '' or 'Points Possible' in row[0], "2nd and 3rd rows should be part of the header"
        else:
            name = row[0]
            sn = row[rsn]
            dorow = True
            if name == 'Test Student':
                dorow = False
            if dorow:
                assert len(name) > 0, "Student name is empty"
                assert len(sn) == 8, "Student number is not 8 characters"
                code = myhash(sn)
                oldcode = row[rcode]
                if (oldcode):
                    # strip commas and trailing decimals added by canvas
                    oldcode = oldcode.replace(',', '')
                    # TODO: regex to remove all trailing zeros would be less fragile
                    oldcode = oldcode.replace('.00', '')
                    oldcode = oldcode.replace('.0', '')
                if oldcode == code:
                    sns[sn] = code
                    print('  row {0}: already had (correct) code {1} for {2} "{3}"'.format( \
                        i, oldcode, sn, name))
                elif oldcode == '':
                    row[rcode] = code
                    sns[sn] = code
                    print('  row {0}: adding code {3} for {2} "{1}"'.format( \
                        i, name, sn, row[rcode]))
                else:
                    print('  row {0}: oops sn {1} "{2}" already had code {3}'.format( \
                        i, sn, name, oldcode))
                    print('    (We tried to assign new code {0})'.format(code))
                    print('    HAVE YOU CHANGED THE SALT SINCE LAST TEST?')
                    raise ValueError('old return code has changed')
        writer.writerow(row)
    return sns


def canvas_csv_check_pdf(sns):
    print('Checking that each codedReturn paper has a corresponding student in the canvas sheet...')
    for file in os.scandir('codedReturn'):
        if file.name.endswith(".pdf"):
            # TODO: this looks rather fragile!
            parts = file.name.partition('_')[2].partition('.')[0]
            sn, meh, code = parts.partition('_')
            if sns.get(sn) == code:
                print('  Good: paper {2} has entry in spreadsheet {0}, {1}'.format(
                    sn, code, file.name))
                sns.pop(sn)
            else:
                print('  ***************************************************************')
                print('  Bad: we found a pdf file that has no student in the spreadsheet')
                print('    Filename: {0}'.format(file.name))
                print('  ***************************************************************')
                #sys.exit()

    # anyone that has a pdf file has been popped from the dict, report the remainders
    if len(sns) == 0:
        print('Everyone listed in the canvas file has a pdf file')
    else:
        print('The following people are in the spreadsheet but do not have a pdf file; did they write?')
        for (sn, code) in sns.items():
            # TODO: name rank and serial number would be good
            print('  SN: {0}, code: {1}'.format(sn, code))


# TODO: maybe pytest makes this?
def raises(expectedException, code=None):
    """Check some lambda expression raises a particular Exception"""
    try:
        code()
    except expectedException:
        return
    raise Failed("DID NOT RAISE")


# TODO: refactor these into proper unit tests
def test_csv():
    print("""
    *** Running tests ***

    Its normal for some verbose output to appear below.  But there should be
    no Exceptions and it should ens with "All tests passed".
    """)

    # general test
    s1 = """Student,SIS User ID,SIS Login ID,Student Number,Midterm1,Return Code (241017),Assignments
,,,,,,Muted,,
    Points Possible,,,,,40,50,999999999999,(read only)
John Smith,12345678,ABCDEFGHIJ01,12345678,34,,49
Test Student,,bbbc6740f0b946af,,,0
"""
    s2 = """Student,SIS User ID,SIS Login ID,Student Number,Midterm1,Return Code (241017),Assignments
,,,,,,Muted,,
    Points Possible,,,,,40,50,999999999999,(read only)
John Smith,12345678,ABCDEFGHIJ01,12345678,34,351525727036,49
Test Student,,bbbc6740f0b946af,,,0
"""
    infile = StringIO(s1)
    outfile = StringIO('')
    sns = _canvas_csv_add_return_codes(infile, outfile);
    s = outfile.getvalue()
    assert s == s2 or s.replace('\r\n', '\n') == s2

    # return codes already exist
    infile = StringIO(s2)
    outfile = StringIO('')
    sns = _canvas_csv_add_return_codes(infile, outfile);
    s = outfile.getvalue()
    assert s == s2 or s.replace('\r\n', '\n') == s2

    # quotes, commas and decimals
    s1 = """Student,SIS User ID,Return Code ()
,,
,,
A Smith,12345678,"351,525,727,036.0"
B Smith,12348888,"480,698,598,264.00"
C Smith,12347777,525156685030.0
D Smith,12346666,347453551559.00
"""
    infile = StringIO(s1)
    outfile = StringIO('')
    sns = _canvas_csv_add_return_codes(infile, outfile);
    s = outfile.getvalue()
    assert s == s1 or s.replace('\r\n', '\n') == s1

    # changing return code is an error
    infile = StringIO("""Student,SIS User ID,Return Code ()
,,
,,
John Smith,12345678,111111111111
""")
    outfile = StringIO('')
    raises(ValueError, lambda: _canvas_csv_add_return_codes(infile, outfile))

    # missing "Student" header
    infile = StringIO("""xxStudentxx,SIS User ID,Return Code ()""")
    outfile = StringIO('')
    raises(AssertionError, lambda: _canvas_csv_add_return_codes(infile, outfile))

    # missing "SIS User ID" header
    infile = StringIO("""Student,SISTER User IDLE,Return Code ()""")
    outfile = StringIO('')
    raises(ValueError, lambda: _canvas_csv_add_return_codes(infile, outfile))

    # can't find "return code"
    infile = StringIO("""Student,SIS User ID,Retrun C0de ()""")
    outfile = StringIO('')
    raises(AssertionError, lambda: _canvas_csv_add_return_codes(infile, outfile))

    # student number too long
    infile = StringIO("""Student,SIS User ID,Return Code ()
,,
,,
John Smith,12345678910,
""")
    outfile = StringIO('')
    raises(AssertionError, lambda: _canvas_csv_add_return_codes(infile, outfile))

    # empty student name
    infile = StringIO("""Student,SIS User ID,Return Code ()
,,
,,
John Smith,12345678,
,12348888,
""")
    outfile = StringIO('')
    raises(AssertionError, lambda: _canvas_csv_add_return_codes(infile, outfile))

    # missing header rows
    infile = StringIO("""Student,SIS User ID,Return Code ()
John Smith,12345678,
""")
    outfile = StringIO('')
    raises(AssertionError, lambda: _canvas_csv_add_return_codes(infile, outfile))

    print("""
    *** All tests passed ***
    """)

    return True
