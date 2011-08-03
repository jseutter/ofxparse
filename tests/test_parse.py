from BeautifulSoup import BeautifulStoneSoup
from datetime import datetime, timedelta
from decimal import Decimal
from unittest import TestCase
from StringIO import StringIO
import sys
sys.path.append('..')

from support import open_file
from ofxparse import OfxParser, AccountType, Account, Statement, Transaction
from ofxparse.ofxparse import OfxFile


class TestOfxFile(TestCase):
    def testHeaders(self):
        expect = { "OFXHEADER": u"100",
                   "DATA": u"OFXSGML",
                   "VERSION": u"102",
                   "SECURITY": None,
                   "ENCODING": u"USASCII",
                   "CHARSET": u"1252",
                   "COMPRESSION":None,
                   "OLDFILEUID": None,
                   "NEWFILEUID": None,
                   }
        ofx = OfxParser.parse(open_file('bank_medium.ofx'))
        self.assertEquals(expect, ofx.headers)


    def testUTF8(self):
        fh = StringIO("""OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:UNICODE
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE

""")
        ofx_file = OfxFile(fh)
        headers = ofx_file.headers
        data = ofx_file.fh.read()
        
        self.assertTrue(type(data) is unicode)
        for key, value in headers.iteritems():
            self.assertTrue(type(key) is unicode)
            self.assertTrue(type(value) is not str)


    def testCP1252(self):
        fh = StringIO("""OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET: 1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE
""")
        ofx_file = OfxFile(fh)
        headers = ofx_file.headers
        result = ofx_file.fh.read()
        
        self.assertTrue(type(result) is unicode)
        for key, value in headers.iteritems():
            self.assertTrue(type(key) is unicode)
            self.assertTrue(type(value) is not str)

    def testBrokenLineEndings(self):
        fh = StringIO("OFXHEADER:100\rDATA:OFXSGML\r")
        ofx_file = OfxFile(fh)
        self.assertEquals(len(ofx_file.headers.keys()), 2)

class TestParse(TestCase):
    def testThatParseWorksWithoutErrors(self):
        OfxParser.parse(open_file('bank_medium.ofx'))

    def testThatParseFailsIfNothingToParse(self):
        self.assertRaises(TypeError, OfxParser.parse, None)

    def testThatParseFailsIfAPathIsPassedIn(self):
        # A file handle should be passed in, not the path.
        self.assertRaises(RuntimeError, OfxParser.parse, '/foo/bar')
    
    def testThatParseReturnsAResultWithABankAccount(self):
        ofx = OfxParser.parse(open_file('bank_medium.ofx'))
        self.assertTrue(ofx.account != None)
    
    def testEverything(self):
        ofx = OfxParser.parse(open_file('bank_medium.ofx'))
        self.assertEquals('12300 000012345678', ofx.account.number)
        self.assertEquals('160000100', ofx.account.routing_number)
        self.assertEquals(Decimal('382.34'), ofx.account.statement.balance)
        # Todo: support values in decimal or int form.
        #self.assertEquals('15', ofx.bank_account.statement.balance_in_pennies)
        self.assertEquals(Decimal('682.34'), ofx.account.statement.available_balance)
        self.assertEquals(datetime(2009, 4, 1), ofx.account.statement.start_date)
        self.assertEquals(datetime(2009, 5, 23, 12, 20, 17), ofx.account.statement.end_date)
        
        self.assertEquals(3, len(ofx.account.statement.transactions))
        
        transaction = ofx.account.statement.transactions[0]
        self.assertEquals("MCDONALD'S #112", transaction.payee)
        self.assertEquals('pos', transaction.type)
        self.assertEquals(Decimal('-6.60'), transaction.amount)
        # Todo: support values in decimal or int form.
        #self.assertEquals('15', transaction.amount_in_pennies)

class TestParseStmtrs(TestCase):
    input = '''
<STMTRS><CURDEF>CAD<BANKACCTFROM><BANKID>160000100<ACCTID>12300 000012345678<ACCTTYPE>CHECKING</BANKACCTFROM>
<BANKTRANLIST><DTSTART>20090401<DTEND>20090523122017
<STMTTRN><TRNTYPE>POS<DTPOSTED>20090401122017.000[-5:EST]<TRNAMT>-6.60<FITID>0000123456782009040100001<NAME>MCDONALD'S #112<MEMO>POS MERCHANDISE;MCDONALD'S #112</STMTTRN>
</BANKTRANLIST><LEDGERBAL><BALAMT>382.34<DTASOF>20090523122017</LEDGERBAL><AVAILBAL><BALAMT>682.34<DTASOF>20090523122017</AVAILBAL></STMTRS>
    '''
    
    def testThatParseStmtrsReturnsAnAccount(self):
        stmtrs = BeautifulStoneSoup(self.input)
        account = OfxParser.parseStmtrs(stmtrs.find('stmtrs'), AccountType.Bank)
        self.assertEquals('12300 000012345678', account.number)
        self.assertEquals('160000100', account.routing_number)
    
    def testThatReturnedAccountAlsoHasAStatement(self):
        stmtrs = BeautifulStoneSoup(self.input)
        account = OfxParser.parseStmtrs(stmtrs.find('stmtrs'), AccountType.Bank)
        self.assertTrue(hasattr(account, 'statement'))
        
class TestAccount(TestCase):
    def testThatANewAccountIsValid(self):
        account = Account()
        self.assertEquals('', account.number)
        self.assertEquals('', account.routing_number)
        self.assertEquals(None, account.statement)
        
class TestParseStatement(TestCase):
    def testThatParseStatementReturnsAStatement(self):
        input = '''
<STMTTRNRS><TRNUID>20090523122017<STATUS><CODE>0<SEVERITY>INFO<MESSAGE>OK</STATUS>
<STMTRS><CURDEF>CAD<BANKACCTFROM><BANKID>160000100<ACCTID>12300 000012345678<ACCTTYPE>CHECKING</BANKACCTFROM>
<BANKTRANLIST><DTSTART>20090401<DTEND>20090523122017
<STMTTRN><TRNTYPE>POS<DTPOSTED>20090401122017.000[-5:EST]<TRNAMT>-6.60<FITID>0000123456782009040100001<NAME>MCDONALD'S #112<MEMO>POS MERCHANDISE;MCDONALD'S #112</STMTTRN>
</BANKTRANLIST><LEDGERBAL><BALAMT>382.34<DTASOF>20090523122017</LEDGERBAL><AVAILBAL><BALAMT>682.34<DTASOF>20090523122017</AVAILBAL></STMTRS></STMTTRNRS>
        '''
        txn = BeautifulStoneSoup(input)
        statement = OfxParser.parseStatement(txn.find('stmttrnrs'))
        self.assertEquals(datetime(2009, 4, 1), statement.start_date)
        self.assertEquals(datetime(2009, 5, 23, 12, 20, 17), statement.end_date)
        self.assertEquals(1, len(statement.transactions))
        self.assertEquals(Decimal('382.34'), statement.balance)
        self.assertEquals(Decimal('682.34'), statement.available_balance)

class TestStatement(TestCase):
    def testThatANewStatementIsValid(self):
        statement = Statement()
        self.assertEquals('', statement.start_date)
        self.assertEquals('', statement.end_date)
        self.assertEquals(0, len(statement.transactions))

class TestParseTransaction(TestCase):
    def testThatParseTransactionReturnsATransaction(self):
        input = '''
        <STMTTRN><TRNTYPE>POS<DTPOSTED>20090401122017.000[-5:EST]<TRNAMT>-6.60<FITID>0000123456782009040100001<NAME>MCDONALD'S #112<MEMO>POS MERCHANDISE;MCDONALD'S #112</STMTTRN>
        '''
        txn = BeautifulStoneSoup(input)
        transaction = OfxParser.parseTransaction(txn.find('stmttrn'))
        self.assertEquals('pos', transaction.type)
        self.assertEquals(datetime(2009, 4, 1, 12, 20, 17) - timedelta(hours=-5), transaction.date)
        self.assertEquals(Decimal('-6.60'), transaction.amount)
        self.assertEquals('0000123456782009040100001', transaction.id)
        self.assertEquals("MCDONALD'S #112", transaction.payee)
        self.assertEquals("POS MERCHANDISE;MCDONALD'S #112", transaction.memo)

class TestTransaction(TestCase):
    def testThatAnEmptyTransactionIsValid(self):
        t = Transaction()
        self.assertEquals('', t.payee)
        self.assertEquals('', t.type)
        self.assertEquals(None, t.date)
        self.assertEquals(None, t.amount)
        self.assertEquals('', t.id)
        self.assertEquals('', t.memo)

class TestInvestmentAccount(TestCase):
    sample = '''
<?xml version="1.0" encoding="UTF-8" ?>
<?OFX OFXHEADER="200" VERSION="200" SECURITY="NONE"
  OLDFILEUID="NONE" NEWFILEUID="NONE" ?>
<OFX>
 <INVSTMTMSGSRSV1>
  <INVSTMTTRNRS>
   <TRNUID>38737714201101012011062420110624</TRNUID>
   <STATUS>
    <CODE>0</CODE>
    <SEVERITY>INFO</SEVERITY>
   </STATUS>
   <INVSTMTRS>
   </INVSTMTRS>
  </INVSTMTTRNRS>
 </INVSTMTMSGSRSV1>
</OFX>
'''
    def testThatParseCanCreateAnInvestmentAccount(self):
        OfxParser.parse(StringIO(self.sample))
        #Success!
