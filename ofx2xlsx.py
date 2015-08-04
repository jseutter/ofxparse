from ofxparse import OfxParser
import pandas as pd

import argparse
parser = argparse.ArgumentParser(description='Convert multiple .qfx or .ofx to'
                                             ' .xlsx, remove duplicate'
                                             ' transactions.')
parser.add_argument('files', metavar='INPUT-Q/OFX-FILE', type=str, nargs='+',
                   help='.qfx or .ofx file names')
parser.add_argument('--start', type=str, metavar='START-DATE',
                   help="Don't take transaction before this date")
parser.add_argument('--end', type=str, metavar='END-DATE',
                   help="Don't take transaction after this date")
parser.add_argument('--output', metavar='XLSX-FILE', type=str,
                    default='output.xlsx', help='Were to store the xlsx')
parser.add_argument('--id-length', metavar='N', type=int, default=24,
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

# TODO automatically extract from transactions
fields = ['id','type', 'date', 'memo', 'payee', 'amount', 'checknum', 'mcc']

data = {}
for fname in args.files:
    ofx = OfxParser.parse(file(fname))
    for account in ofx.accounts:
        df = data.get(account.number, pd.DataFrame(columns=fields+['fname']))
        for transaction in account.statement.transactions:
            s = pd.Series([getattr(transaction,f) for f in fields], index=fields)
            s['fname'] = fname.split('/')[-1]
            df = df.append(s, ignore_index=True)
        df['id'] = df['id'].str[:args.id_length]  # clip the last part of the ID which changes from download to download
        data[account.number] = df

print "Writing result to", args.output
writer = pd.ExcelWriter(args.output)

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
