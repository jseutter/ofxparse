from BeautifulSoup import BeautifulStoneSoup
import codecs

class OfxFile(object):
    def __init__(self, fh):
        self.headers = {}
        self.fh = fh
        self.read_headers()

    def read_headers(self):
        if not hasattr(self.fh, "seek") or not hasattr(self.fh, "next"):
            return # fh is not a file object, we're doomed.

        orig_pos = self.fh.tell()
        self.fh.seek(0)
        
        for line in self.fh:
            # Newline?
            if line.strip() == "":
                break
            
            header, value = line.split(":")
            header, value = header.strip().upper(), value.strip()

            if value.upper() == "NONE":
                value = None

            self.headers[header] = value
            
        # Look for the encoding
        enc_type = self.headers.get("ENCODING")
        if enc_type:
            encoding = None # Unknown

            if enc_type == "USASCII":
                cp = self.headers.get("CHARSET", "1252")
                encoding = "cp%s" % (cp, )

            elif enc_type == "UNICODE":
                encoding = "utf-8"
            
            try:
                codec = codecs.lookup(encoding)
            except LookupError:
                encoding = None

            if encoding:
                self.fh = codec.streamreader(self.fh)

                # Decode the headers
                uheaders = {}
                for key,value in self.headers.iteritems():
                    key = key.decode(encoding)

                    if type(value) is str:
                        value = value.decode(encoding)
                    
                    uheaders[key] = value
                self.headers = uheaders
        # Reset the fh to the original position
        self.fh.seek(orig_pos)

class Ofx(object):
    pass

class Account(object):
    def __init__(self):
        self.number = ''
        self.routing_number = ''
        self.statement = None

class Statement(object):
    def __init__(self):
        self.start_date = ''
        self.end_date = ''
        self.transactions = []

class Transaction(object):
    def __init__(self):
        self.name = ''
        self.type = ''
        self.date = ''
        self.amount = ''
        self.id = ''
        self.memo = ''

class Institution(object):
    pass

class OfxParser(object):
    @classmethod
    def parse(cls_, file_handle):
        if isinstance(file_handle, type('')):
            raise RuntimeError("parse() takes in a file handle, not a string")

        ofx_obj = Ofx()

        # Store the headers
        ofx_file = OfxFile(file_handle)
        ofx_obj.headers = ofx_file.headers

        ofx = BeautifulStoneSoup(ofx_file.fh)
        stmtrs_ofx = ofx.find('stmtrs')
        if stmtrs_ofx:
            ofx_obj.bank_account = cls_.parseStmtrs(stmtrs_ofx)
        return ofx_obj

    @classmethod
    def parseStmtrs(cls_, stmtrs_ofx):
        ''' Parse the <STMTRS> tag and return an Account object. '''
        account = Account()
        acctid_tag = stmtrs_ofx.find('acctid')
        if hasattr(acctid_tag, 'contents'):
            account.number = acctid_tag.contents[0]
        bankid_tag = stmtrs_ofx.find('bankid')
        if hasattr(bankid_tag, 'contents'):
            account.routing_number = bankid_tag.contents[0]

        if stmtrs_ofx:
            account.statement = cls_.parseStatement(stmtrs_ofx)
        return account
    
    @classmethod
    def parseStatement(cls_, stmt_ofx):
        '''
        Parse a statement in ofx-land and return a Statement object.
        '''
        statement = Statement()
        dtstart_tag = stmt_ofx.find('dtstart')
        if hasattr(dtstart_tag, "contents"):
            statement.start_date = dtstart_tag.contents[0]
        dtend_tag = stmt_ofx.find('dtend')
        if hasattr(dtend_tag, "contents"):
            statement.end_date = dtend_tag.contents[0].strip()
        ledger_bal_tag = stmt_ofx.find('ledgerbal')
        if hasattr(ledger_bal_tag, "contents"):
            balamt_tag = ledger_bal_tag.find('balamt')
            if hasattr(balamt_tag, "contents"):
                statement.balance = balamt_tag.contents[0]
        avail_bal_tag = stmt_ofx.find('availbal')
        if hasattr(avail_bal_tag, "contents"):
            balamt_tag = avail_bal_tag.find('balamt')
            if hasattr(balamt_tag, "contents"):
                statement.available_balance = balamt_tag.contents[0]
        for transaction_ofx in stmt_ofx.findAll('stmttrn'):
            statement.transactions.append(cls_.parseTransaction(transaction_ofx))
        return statement

    @classmethod
    def parseTransaction(cls_, txn_ofx):
        '''
        Parse a transaction in ofx-land and return a Transaction object.
        '''
        transaction = Transaction()

        type_tag = txn_ofx.find('trntype')
        if hasattr(type_tag, 'contents'):
            transaction.type = type_tag.contents[0].lower()

        name_tag = txn_ofx.find('name')
        if hasattr(name_tag, "contents"):
            transaction.payee = name_tag.contents[0]

        memo_tag = txn_ofx.find('memo')
        if hasattr(memo_tag, "contents"):
            transaction.memo = memo_tag.contents[0]

        amt_tag = txn_ofx.find('trnamt')
        if hasattr(amt_tag, "contents"):
            transaction.amount = amt_tag.contents[0]

        date_tag = txn_ofx.find('dtposted')
        if hasattr(date_tag, "contents"):
            transaction.date = date_tag.contents[0]

        id_tag = txn_ofx.find('fitid')
        if hasattr(id_tag, "contents"):
            transaction.id = id_tag.contents[0]

        return transaction
