#!/usr/bin/env python3
import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")

from ofxparse.ofxtodataframe import ofx_to_dataframe
import pandas as pd
from pandas import ExcelWriter
import sys
import argparse
from io import StringIO

# ToDo: Remove duplicate transactions from different files
parser = argparse.ArgumentParser(description='Convert multiple .qfx or .ofx to'
                                             ' .xlsx or csv.\n')
parser.add_argument('files', type=argparse.FileType('r'), nargs='+',   #;metavar='*.ofx *.qfx', default=[], type=str, nargs='+',
help='.qfx or .ofx file names')
parser.add_argument('--start', type=str, metavar='1700-01-01',
                    default='1700-01-01',
                    help="Don't take transaction before this date")
parser.add_argument('--end', type=str, metavar='3000-12-31',
                    default='3000-12-31',
                    help="Don't take transaction after this date")
parser.add_argument('-o', '--output', metavar='output.csv', type=str,
                    default='output.csv', help='Were to store the output. Extension determines output format')
parser.add_argument('--id-length', metavar='24', type=int, default=24,
                    help='Truncate the number of digits in a transaction ID.'
                    ' This is important because this program remove'
                    ' transactions with duplicate IDs (after verifing'
                    ' that they are identical.'
                    ' If you feel unsafe then use a large number but'
                    'usually the last digits of the transaction ID are'
                    'running numbers which change from download to download'
                    ' as a result you will have duplicate transactions'
                    ' unless you truncate the ID.')


args = parser.parse_args()
if 'stdin' in args.files[0].name:
    fp=args.files[0]
    args.files=[StringIO(fp.read())]
data = ofx_to_dataframe(args.files)

if 'csv' in args.output:
    outstring = ""
    for key,df in data.items():
        outstring += "##### {}\n".format(key) + df.to_csv(None, index=False, header=True)
    if args.output=='output.csv':
        print(outstring)
    with open(args.output, 'w') as fileobj:
        print(outstring, file=fileobj)
elif 'xlsx' in args.output:
    writer = pd.ExcelWriter(args.output)
    for key,df in data.items():
        df.to_excel(writer, sheet_name=key)
    writer.save()

__dev_notes__ = '''
for account_number, df in data.iteritems():
    # A transaction is identified using all `fields`
    # collapse all repeated transactions from the same file into one row
    # find the number of repeated transactions and
    # put it in samedayrepeat column
    df_count = df.groupby(fields+['fname']).size()
    df_count = df_count.reset_index()
    df_count.columns = list(df_count.columns[:-1]) + ['samedayrepeat']

    # two transactions from the same file are always different
    # but the same transaction can appear in multiple files if they overlap.
    # check we have the same samedayrepeat for the same transaction on different files
    df_size_fname_count = df_count.reset_index().groupby(fields).samedayrepeat.nunique()
    assert (df_size_fname_count == 1).all(), "Different samedayrepeat in different files"

    # take one file as an example
    df1 = df_count.reset_index().groupby(fields+['samedayrepeat']).first()
    df1 = df1.reset_index()

    # expand back the collapsed transactions
    # duplicate rows according to samedayrepeat value
    df2 = df1.copy()
    for i in range(2,df1.samedayrepeat.max()+1):
        df2 = df2.append(df1[i<=df1.samedayrepeat])

    # sort according to date
    df2 = df2.reset_index().set_index('date').sort_index()
    # filter dates
    df2 = df2.ix[args.start:args.end]

    #cleanup
    df2 = df2.reset_index()[fields]

    df2.to_excel(writer, account_number, index=False)

writer.save()
'''
