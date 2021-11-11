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
        security_map = {}
        if hasattr(ofx, 'security_list'):
            security_map.update({x.uniqueid : x.ticker for x in ofx.security_list})
        # different transaction types have different fields. So we create df for each txn_type
        # and append the contents of each txn into appropriate df
        for account in ofx.accounts:
            for transaction in account.statement.transactions + \
                (hasattr(account.statement, 'positions') and account.statement.positions or []):
                txn_type = type(transaction).__name__
                transaction.acctnum = account.number
                if not txn_type in data:
                    fields = [x for x in dir(transaction) if not x.startswith('_')]
                    data[txn_type] = pd.DataFrame(columns=fields)
                df = data[txn_type]
                fields = set(df.columns)
                sr = pd.Series({f: getattr(transaction,f) for f in fields})
                data[txn_type] = df.append(sr, ignore_index=True)

            # add cash balance as a "Cash" position
            cash_amount = None
            if hasattr(account.statement, 'balance'):
                cash_amount = account.statement.balance
                dt = account.statement.balance_date
            elif hasattr(account.statement, 'available_cash'):
                cash_amount = account.statement.available_cash
                dt = account.statement.end_date
            if cash_amount is not None:
                df = data.get('Position',
                              pd.DataFrame(columns=['date', 'market_value', 'security', 'unit_price', 'units', 'acctnum']))
                sr = pd.Series({
                    'date'        : dt,
                    'security'    : account.curdef,
                    'market_value': cash_amount,
                    'units'       : cash_amount,
                    'unit_price'  : decimal.Decimal('1.00'),
                    'acctnum'     : account.number})
                data['Position'] = df.append(sr, ignore_index=True)

        # add fname info into each df. Truncate ID if needed
        for key,df in data.items():
            df['fname'] = hasattr(fileobj, 'name') and fileobj.name or 'stdin'
            if 'id' in df.columns:
                df['id'] = df['id'].str[:id_len]  # clip the last part of the ID which changes from download to download
            if 'security' in df.columns:
                df['security'] = df['security'].apply(lambda x: security_map.get(x, x))
            if 'AGGREGATE_TYPES' in df.columns :
                del df['AGGREGATE_TYPES']
            if key in collected_df:
                collected_df[key] = collected_df[key].append(df, ignore_index=True)
            else:
                collected_df[key] = df
    return collected_df

__dev_notes__='''
For brokerage, balances are available in account.statement.balance_list... but overall cash is also summarized in account.statement.available_cash corresponding to statement.end_date
For bank, balance is available in account.statement.balance (and balance_date)

'''
