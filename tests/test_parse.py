from unittest import TestCase
from BeautifulSoup import BeautifulStoneSoup
import sys
sys.path.append('..')
from ofx_parse import *

class TestParse(TestCase):
    def testThatParseWorksWithoutErrors(self):
        ofx = OfxParser.parse(file('fixtures/bank_small.ofx'))
        ofx = OfxParser.parse(file('fixtures/bank_medium.ofx'))
    
    def testThatParseReturnsAResultWithABankAccount(self):
        ofx = OfxParser.parse(file('fixtures/bank_medium.ofx'))
        self.assertTrue(ofx.bank_account != None)
    
    def testEverything(self):
        ofx = OfxParser.parse(file('fixtures/bank_medium.ofx'))
        self.assertEquals('12300 000012345678', ofx.bank_account.number)
        self.assertEquals('160000100', ofx.bank_account.routing_number)
        self.assertEquals('382.34', ofx.bank_account.statement.balance)
        # Todo: support values in decimal or int form.
        #self.assertEquals('15', ofx.bank_account.statement.balance_in_pennies)
        self.assertEquals('682.34', ofx.bank_account.statement.available_balance)
        self.assertEquals('20090401', ofx.bank_account.statement.start_date)
        self.assertEquals('20090523122017', ofx.bank_account.statement.end_date)
        
        self.assertEquals(3, len(ofx.bank_account.statement.transactions))
        
        transaction = ofx.bank_account.statement.transactions[0]
        self.assertEquals("MCDONALD'S #112", transaction.payee)
        self.assertEquals('pos', transaction.type)
        self.assertEquals('-6.60', transaction.amount)
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
        account = OfxParser.parseStmtrs(stmtrs.find('stmtrs'))
        self.assertEquals('12300 000012345678', account.number)
        self.assertEquals('160000100', account.routing_number)
    
    def testThatReturnedAccountAlsoHasAStatement(self):
        stmtrs = BeautifulStoneSoup(self.input)
        account = OfxParser.parseStmtrs(stmtrs.find('stmtrs'))
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
        self.assertEquals('20090401', statement.start_date)
        self.assertEquals('20090523122017', statement.end_date)
        self.assertEquals(1, len(statement.transactions))
        self.assertEquals('382.34', statement.balance)
        self.assertEquals('682.34', statement.available_balance)

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
        self.assertEquals('20090401122017.000[-5:EST]', transaction.date)
        self.assertEquals('-6.60', transaction.amount)
        self.assertEquals('0000123456782009040100001', transaction.id)
        self.assertEquals("MCDONALD'S #112", transaction.payee)
        self.assertEquals("POS MERCHANDISE;MCDONALD'S #112", transaction.memo)

class TestTransaction(TestCase):
    def testThatAnEmptyTransactionIsValid(self):
        t = Transaction()
        self.assertEquals('', t.type)
        self.assertEquals('', t.date)
        self.assertEquals('', t.amount)
        self.assertEquals('', t.id)
        self.assertEquals('', t.name)
        self.assertEquals('', t.memo)

