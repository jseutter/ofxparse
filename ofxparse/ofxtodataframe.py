from ofxparse import OfxParser
import pandas as pd
import codecs
import os.path as path
import sys, warnings
import decimal

# fields of transactions are auto extracted using dir(transactiontype)-{attributes starting with '_'}

def ofx_to_dataframe(fileobjs, id_len=24):
    collected_df={}
    assert(isinstance(fileobjs, list))
    for fileobj in fileobjs:
        data = {}

        #with codecs.open(fname) as fileobj:
        #    ofx = OfxParser.parse(fileobj)
        ofx = OfxParser.parse(fileobj)
        # it seems one ofx file contains only one securities list. Create a mapping from ID to ticker
        if hasattr(ofx, 'security_list'):
            security_map = {x.uniqueid : x.ticker for x in ofx.security_list}
        # different transaction types have different fields. So we create df for each txn_type
        # and append the contents of each txn into appropriate df
        for account in ofx.accounts:
            for transaction in account.statement.transactions + \
                (hasattr(account.statement, 'positions') and account.statement.positions or []):
                txn_type = type(transaction).__name__
                if not txn_type in data:
                    fields = [x for x in dir(transaction) if not x.startswith('_')]
                    data[txn_type] = pd.DataFrame(columns=fields)
                df = data[txn_type]
                fields = set(df.columns)
                sr = pd.Series([getattr(transaction,f) for f in fields], index=fields)
                sr = pd.Series({f:transaction.f} for f in fields)
                sr['acctnum'] = account.number
                data[txn_type] = df.append(sr, ignore_index=True)
            if hasattr(account, 'balance'):
                txn_type = 'Positions'
                if not txn_type in data:
                    fields = ['date', 'market_value', 'security', 'unit_price', 'units']
                    data[txn_type] = pd.DataFrame(columns=fields)
                df = data[txn_type]
                fields = set(df.columns)
                sr = pd.Series({
                    'date'       :statement.end_date,
                    'security'   : 'Cash',
                    'units'      :statement.balance,
                    'unit_price' : decimal.Decimal('1.00')}, index=fields)
                sr['acctnum'] = account.number
                data[txn_type] = df.append(sr, ignore_index=True)

        # add fname info into each df. Truncate ID if needed
        for key,df in data.items():
            df['fname'] = hasattr(fileobj, 'name') and fileobj.name or 'stdin'
            if 'id' in df.columns:
                df['id'] = df['id'].str[:id_len]  # clip the last part of the ID which changes from download to download
            if 'security' in df.columns:
                df['security'] = df['security'].apply(lambda x: security_map[x])
            if 'AGGREGATE_TYPES' in df.columns :
                del df['AGGREGATE_TYPES']
            if key in collected_df:
                collected_df[key] = collected_df[key].append(df, ignore_index=True)
            else:
                collected_df[key] = df
    return collected_df
