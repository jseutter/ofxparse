from BeautifulSoup import BeautifulStoneSoup
import decimal, datetime
import codecs
import re


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
        
        head_data = self.fh.read(1024*10)
        head_data = head_data[:head_data.find('<')]
        
        for line in re.split('\r?\n?', head_data):
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

class AccountType(object):
    (Unknown, Bank, CreditCard, Investment) = range(0, 4)

class Account(object):
    def __init__(self):
        self.statement = None
        self.number = ''
        self.routing_number = ''
        self.institution = None
        self.type = AccountType.Unknown
        # Used for error tracking
        self.warnings = []

class InvestmentAccount(Account):
    def __init__(self):
        super(InvestmentAccount, self).__init__()
        self.brokerid = ''

class Security:
    def __init__(self, uniqueid, name, ticker, memo):
        self.uniqueid = uniqueid
        self.name = name
        self.ticker = ticker
        self.memo = memo

class Statement(object):
    def __init__(self):
        self.start_date = ''
        self.end_date = ''
        self.currency = ''
        self.transactions = []
        # Error tracking:
        self.discarded_entries = []
        self.warnings = []

class InvestmentStatement(object):
    def __init__(self):
        self.positions = []
        self.transactions = []
        # Error tracking:
        self.discarded_entries = []
        self.warnings = []

class Transaction(object):
    def __init__(self):
        self.payee = ''
        self.type = ''
        self.date = None
        self.amount = None
        self.id = ''
        self.memo = ''
    
    def __repr__(self):
        return "<Transaction units=" + str(self.amount) + ">"

class InvestmentTransaction(object):
    def __init__(self):
        self.tradeDate = None
        self.settleDate = None
        self.security = ''
        self.units = decimal.Decimal(0)
        self.unit_price = decimal.Decimal(0)
    
    def __repr__(self):
        return "<InvestmentTransaction units=" + str(self.units) + ">"

class Position(object):
    def __init__(self):
        self.security = ''
        self.units = decimal.Decimal(0)
        self.unit_price = decimal.Decimal(0)

class Institution(object):
    def __init__(self):
        self.organization = ''

class OfxParserException(Exception):
    pass

class OfxParser(object):
    @classmethod
    def parse(cls_, file_handle, fail_fast = True):
        '''
        parse is the main entry point for an OfxParser. It takes a file
        handle and an optional log_errors flag.
        
        If fail_fast is True, the parser will fail on any errors.
        If fail_fast is False, the parser will log poor statements in the
        statement class and continue to run. Note: the library does not
        guarantee that no exceptions will be raised to the caller, only
        that statements will include bad transactions (which are marked).
        
        '''
        cls_.fail_fast = fail_fast
        
        if isinstance(file_handle, type('')):
            raise RuntimeError("parse() takes in a file handle, not a string")

        ofx_obj = Ofx()

        # Store the headers
        ofx_file = OfxFile(file_handle)
        ofx_obj.headers = ofx_file.headers

        ofx = BeautifulStoneSoup(ofx_file.fh)
        stmtrs_ofx = ofx.find('stmtrs')
        if stmtrs_ofx:
            ofx_obj.account = cls_.parseStmtrs(stmtrs_ofx, AccountType.Bank)
            org_ofx = ofx.find('org')
            if org_ofx:
                ofx_obj.account.institution = cls_.parseOrg(org_ofx)
            return ofx_obj
        ccstmtrs_ofx = ofx.find('ccstmtrs')
        if ccstmtrs_ofx:
            ofx_obj.account = cls_.parseStmtrs(
                ccstmtrs_ofx, AccountType.CreditCard)
            org_ofx = ofx.find('org')
            if org_ofx:
                ofx_obj.account.institution = cls_.parseOrg(org_ofx)
            return ofx_obj
        invstmtrs_ofx = ofx.find('invstmtrs')
        if invstmtrs_ofx:
            ofx_obj.account = cls_.parseInvstmtrs(invstmtrs_ofx)
            seclist_ofx = ofx.find('seclist')
            if seclist_ofx:
                ofx_obj.security_list = cls_.parseSeclist(seclist_ofx)
            else:
                ofx_obj.security_list = None
            return ofx_obj
        return ofx_obj
    
    @classmethod
    def parseOfxDateTime(cls_, ofxDateTime):
        #dateAsString looks something like 20101106160000.00[-5:EST]
        #for 6 Nov 2010 4pm UTC-5 aka EST
        res = re.search("\[(?P<tz>-?\d+)\:\w*\]$", ofxDateTime)
        if res:
            tz = int(res.group('tz'))
        else:
            tz = 0

        timeZoneOffset = datetime.timedelta(hours=tz)

        try:
            local_date = datetime.datetime.strptime(
                ofxDateTime[:14], '%Y%m%d%H%M%S'
            )
            return local_date - timeZoneOffset
        except:
            return datetime.datetime.strptime(
                ofxDateTime[:8], '%Y%m%d') - timeZoneOffset

    @classmethod
    def parseInvstmtrs(cls_, invstmtrs_ofx):
        account = InvestmentAccount()
        acctid_tag = invstmtrs_ofx.find('acctid')
        if (hasattr(acctid_tag, 'contents')):
            if cls_.fail_fast or len(acctid_tag.contents) > 0:
                account.number = acctid_tag.contents[0].strip()
            else:
                account.warnings.append("Empty acctid tag for %s" % invstmtrs_ofx)
        brokerid_tag = invstmtrs_ofx.find('brokerid')
        if (hasattr(brokerid_tag, 'contents')):
            if cls_.fail_fast or len(brokerid_tag.contents) > 0:
                account.brokerid = brokerid_tag.contents[0].strip()
            else:
                account.warnings.append("Empty brokerid tag for %s" % invstmtrs_ofx)
        account.type = AccountType.Investment
        
        if (invstmtrs_ofx):
            account.statement = cls_.parseInvestmentStatement(invstmtrs_ofx)
        
        return account
    
    @classmethod
    def parseSeclist(cls_, seclist_ofx):
        securityList = []
        for secinfo_ofx in seclist_ofx.findAll('secinfo'):
            uniqueid_tag = secinfo_ofx.find('uniqueid')
            name_tag = secinfo_ofx.find('secname')
            ticker_tag = secinfo_ofx.find('ticker')
            memo_tag = secinfo_ofx.find('memo')
            if uniqueid_tag and name_tag and ticker_tag and memo_tag:
                securityList.append(
                    Security(uniqueid_tag.contents[0].strip(),
                             name_tag.contents[0].strip(),
                             ticker_tag.contents[0].strip(),
                             memo_tag.contents[0].strip()))
        return securityList

    @classmethod
    def parseInvestmentPosition(cls_, ofx):
        position = Position()
        tag = ofx.find('uniqueid')
        if (hasattr(tag, 'contents')):
            position.security = tag.contents[0].strip()
        tag = ofx.find('units')
        if (hasattr(tag, 'contents')):
            position.units = decimal.Decimal(tag.contents[0].strip())
        tag = ofx.find('unitprice')
        if (hasattr(tag, 'contents')):
            position.unit_price = decimal.Decimal(tag.contents[0].strip())
        tag = ofx.find('dtpriceasof')
        if (hasattr(tag, 'contents')):
            position.date = cls_.parseOfxDateTime(tag.contents[0].strip())
        return position

    @classmethod
    def parseInvestmentTransaction(cls_, ofx):
        transaction = InvestmentTransaction()
        tag = ofx.find('fitid')
        if (hasattr(tag, 'contents')):
            transaction.id = tag.contents[0].strip()
        tag = ofx.find('memo')
        if (hasattr(tag, 'contents')):
            transaction.memo = tag.contents[0].strip()
        tag = ofx.find('dttrade')
        if (hasattr(tag, 'contents')):
            transaction.tradeDate = cls_.parseOfxDateTime(tag.contents[0].strip())
        tag = ofx.find('dtsettle')
        if (hasattr(tag, 'contents')):
            transaction.settleDate = cls_.parseOfxDateTime(tag.contents[0].strip())
        tag = ofx.find('uniqueid')
        if (hasattr(tag, 'contents')):
            transaction.security = tag.contents[0].strip()
        tag = ofx.find('units')
        if (hasattr(tag, 'contents')):
            transaction.units = decimal.Decimal(tag.contents[0].strip())
        tag = ofx.find('unitprice')
        if (hasattr(tag, 'contents')):
            transaction.unit_price = decimal.Decimal(tag.contents[0].strip())
        return transaction

    @classmethod
    def parseInvestmentStatement(cls_, invstmtrs_ofx):
        statement = InvestmentStatement()
        currency_tag = invstmtrs_ofx.find('curdef')
        if hasattr(currency_tag, "contents"):
            statement.currency = currency_tag.contents[0].strip().lower()
        invtranlist_ofx = invstmtrs_ofx.find('invtranlist')
        if (invtranlist_ofx != None):
            tag = invtranlist_ofx.find('dtstart')
            if (hasattr(tag, 'contents')):
                if cls_.fail_fast or len(tag.contents) > 0:
                    statement.start_date = cls_.parseOfxDateTime(
                        tag.contents[0].strip())
                else:
                    statement.warnings.append('Empty start date.')
                    
            tag = invtranlist_ofx.find('dtend')
            if (hasattr(tag, 'contents')):
                if cls_.fail_fast or len(tag.contents) > 0:
                    statement.end_date = cls_.parseOfxDateTime(tag.contents[0].strip())
                else:
                    statement.warnings.append('Empty end date.')
        
        try:
            for investment_ofx in invstmtrs_ofx.findAll('posmf'):
                statement.positions.append(
                    cls_.parseInvestmentPosition(investment_ofx))
        except Exception as e:
            if cls_.fail_fast:
                raise
            statement.discarded_entries.append(
                { 'error': "Positions: " + str(e),
                 'content': investment_ofx }
            )
        
        
        for transaction_type in ['buymf', 'sellmf', 'reinvest']:
            try:
                for investment_ofx in invstmtrs_ofx.findAll(transaction_type):
                    statement.transactions.append(
                        cls_.parseInvestmentTransaction(investment_ofx))
            except Exception as e:
                if cls_.fail_fast:
                    raise
                statement.discarded_entries.append(
                    { 'error': transaction_type + ": " + str(e),
                     'content': investment_ofx }
                )
        
        return statement
    
    @classmethod
    def parseOrg(cls_, org_ofx):
        institution = Institution()
        if hasattr(org_ofx, 'contents'):
            institution.organization = org_ofx.contents[0].strip()
        return institution

    @classmethod
    def parseStmtrs(cls_, stmtrs_ofx, accountType):
        ''' Parse the <STMTRS> tag and return an Account object. '''
        account = Account()
        acctid_tag = stmtrs_ofx.find('acctid')
        if hasattr(acctid_tag, 'contents'):
            account.number = acctid_tag.contents[0].strip()
        bankid_tag = stmtrs_ofx.find('bankid')
        if hasattr(bankid_tag, 'contents'):
            account.routing_number = bankid_tag.contents[0].strip()
        account.type = accountType

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
            if cls_.fail_fast or len(dtstart_tag.contents) > 0:
                statement.start_date = cls_.parseOfxDateTime(
                    dtstart_tag.contents[0].strip())
            else:
                statement.warnings.append("Statement start date was empty for %s" % stmt_ofx)
                
        dtend_tag = stmt_ofx.find('dtend')
        if hasattr(dtend_tag, "contents"):
            if cls_.fail_fast or len(dtend_tag.contents) > 0:
                statement.end_date = cls_.parseOfxDateTime(
                    dtend_tag.contents[0].strip())
            else:
                statement.warnings.append("Statement end date was empty for %s" % stmt_ofx)
                
        currency_tag = stmt_ofx.find('curdef')
        if hasattr(currency_tag, "contents"):
            if cls_.fail_fast or len(currency_tag.contents) > 0:
                statement.currency = currency_tag.contents[0].strip().lower()
            else:
                statement.warnings.append("Currency definition was empty for %s" % stmt_ofx)
                
        ledger_bal_tag = stmt_ofx.find('ledgerbal')
        if hasattr(ledger_bal_tag, "contents"):
            balamt_tag = ledger_bal_tag.find('balamt')
            if hasattr(balamt_tag, "contents"):
                if cls_.fail_fast or len(balamt_tag.contents) > 0:
                    statement.balance = decimal.Decimal(
                        balamt_tag.contents[0].strip())
                else:
                    statement.warnings.append("Ledger balance amount was empty for %s" % stmt_ofx)
                    
        avail_bal_tag = stmt_ofx.find('availbal')
        if hasattr(avail_bal_tag, "contents"):
            balamt_tag = avail_bal_tag.find('balamt')
            if hasattr(balamt_tag, "contents"):
                if cls_.fail_fast or len(balamt_tag.contents) > 0:
                    statement.available_balance = decimal.Decimal(
                        balamt_tag.contents[0].strip())
                else:
                    statement.warnings.append("Available balance amount was empty for %s" % stmt_ofx)
                    
        for transaction_ofx in stmt_ofx.findAll('stmttrn'):
            try:
                statement.transactions.append(cls_.parseTransaction(transaction_ofx))
            except OfxParserException as ofxError:
                statement.discarded_entries.append({ 'error': str(ofxError), 'content': transaction_ofx })
                if cls_.fail_fast:
                    raise

        return statement

    @classmethod
    def parseTransaction(cls_, txn_ofx):
        '''
        Parse a transaction in ofx-land and return a Transaction object.
        '''
        transaction = Transaction()

        type_tag = txn_ofx.find('trntype')
        if hasattr(type_tag, 'contents'):
            transaction.type = type_tag.contents[0].lower().strip()

        name_tag = txn_ofx.find('name')
        if hasattr(name_tag, "contents"):
            transaction.payee = name_tag.contents[0].strip()

        memo_tag = txn_ofx.find('memo')
        if hasattr(memo_tag, "contents"):
            transaction.memo = memo_tag.contents[0].strip()

        amt_tag = txn_ofx.find('trnamt')
        if hasattr(amt_tag, "contents"):
            try:
                transaction.amount = decimal.Decimal(amt_tag.contents[0].strip())
            except IndexError:
                raise
            except Exception:
                raise OfxParserException("Invalid Transaction Amount: '%s'" % amt_tag.contents[0])
        else:
            raise OfxParserException("Missing Transaction Amount (a required field)")

        date_tag = txn_ofx.find('dtposted')
        if hasattr(date_tag, "contents"):
            try:
                transaction.date = cls_.parseOfxDateTime(
                    date_tag.contents[0].strip())
            except IndexError: 
                raise OfxParserException("Invalid Transaction Date")
            except ValueError as ve:
                raise OfxParserException(str(ve))
        else:
            raise OfxParserException("Missing Transaction Date (a required field)")
        
        id_tag = txn_ofx.find('fitid')
        if hasattr(id_tag, "contents"):
            transaction.id = id_tag.contents[0].strip()
        else:
            raise OfxParserException("Missing FIT id (a required field)")
        
        return transaction

