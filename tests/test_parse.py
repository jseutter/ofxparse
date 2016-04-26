from __future__ import absolute_import

import os
from datetime import datetime, timedelta
from decimal import Decimal
from unittest import TestCase
import sys
sys.path.insert(0, os.path.abspath('..'))

import six

from .support import open_file
from ofxparse import OfxParser, AccountType, Account, Statement, Transaction
from ofxparse.ofxparse import OfxFile, OfxPreprocessedFile, OfxParserException, soup_maker


class TestOfxPreprocessedFile(TestCase):

    def testPreprocess(self):
        fh = six.BytesIO(six.b("""OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE

<OFX><DTASOF><![CDATA[></tricky]]><LEAVE ALONE><VAL.UE>a<VAL_UE>b<TE_ST></TE_ST><TE.ST></TE.ST><INVBAL><BALLIST><BAL><NAME>Net<DTASOF>2222</BAL><BAL><NAME>Gross<DTASOF>3333</BAL></BALLIST></INVBAL></OFX>
"""))
        expect = """OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE

<OFX><DTASOF><![CDATA[></tricky]]><LEAVE ALONE></DTASOF><VAL.UE>a</VAL.UE><VAL_UE>b</VAL_UE><TE_ST></TE_ST><TE.ST></TE.ST><INVBAL><BALLIST><BAL><NAME>Net</NAME><DTASOF>2222</DTASOF></BAL><BAL><NAME>Gross</NAME><DTASOF>3333</DTASOF></BAL></BALLIST></INVBAL></OFX>
"""
        ofx_file = OfxPreprocessedFile(fh)
        data = ofx_file.fh.read()
        self.assertEqual(data, expect)

    def testHeaders(self):
        expect = {"OFXHEADER": six.u("100"),
                  "DATA": six.u("OFXSGML"),
                  "VERSION": six.u("102"),
                  "SECURITY": None,
                  "ENCODING": six.u("USASCII"),
                  "CHARSET": six.u("1252"),
                  "COMPRESSION": None,
                  "OLDFILEUID": None,
                  "NEWFILEUID": None,
                  }
        ofx = OfxParser.parse(open_file('bank_medium.ofx'))
        self.assertEquals(expect, ofx.headers)

    def testUTF8(self):
        fh = six.BytesIO(six.b("""OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:UNICODE
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE

"""))
        ofx_file = OfxPreprocessedFile(fh)
        headers = ofx_file.headers
        data = ofx_file.fh.read()

        self.assertTrue(type(data) is six.text_type)
        for key, value in six.iteritems(headers):
            self.assertTrue(type(key) is six.text_type)
            self.assertTrue(type(value) is not six.binary_type)

    def testCP1252(self):
        fh = six.BytesIO(six.b("""OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET: 1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE
"""))
        ofx_file = OfxPreprocessedFile(fh)
        headers = ofx_file.headers
        result = ofx_file.fh.read()

        self.assertTrue(type(result) is six.text_type)
        for key, value in six.iteritems(headers):
            self.assertTrue(type(key) is six.text_type)
            self.assertTrue(type(value) is not six.binary_type)

    def testUTF8Japanese(self):
        fh = six.BytesIO(six.b("""OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:UTF-8
CHARSET:CSUNICODE
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE
"""))
        ofx_file = OfxPreprocessedFile(fh)
        headers = ofx_file.headers
        result = ofx_file.fh.read()

        self.assertTrue(type(result) is six.text_type)
        for key, value in six.iteritems(headers):
            self.assertTrue(type(key) is six.text_type)
            self.assertTrue(type(value) is not six.binary_type)

    def testBrokenLineEndings(self):
        fh = six.BytesIO(six.b("OFXHEADER:100\rDATA:OFXSGML\r"))
        ofx_file = OfxPreprocessedFile(fh)
        self.assertEquals(len(ofx_file.headers.keys()), 2)


class TestOfxFile(TestCase):
    def testHeaders(self):
        expect = {"OFXHEADER": six.u("100"),
                  "DATA": six.u("OFXSGML"),
                  "VERSION": six.u("102"),
                  "SECURITY": None,
                  "ENCODING": six.u("USASCII"),
                  "CHARSET": six.u("1252"),
                  "COMPRESSION": None,
                  "OLDFILEUID": None,
                  "NEWFILEUID": None,
                  }
        ofx = OfxParser.parse(open_file('bank_medium.ofx'))
        self.assertEquals(expect, ofx.headers)

    def testUTF8(self):
        fh = six.BytesIO(six.b("""OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:UNICODE
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE

"""))
        ofx_file = OfxFile(fh)
        headers = ofx_file.headers
        data = ofx_file.fh.read()

        self.assertTrue(type(data) is six.text_type)
        for key, value in six.iteritems(headers):
            self.assertTrue(type(key) is six.text_type)
            self.assertTrue(type(value) is not six.binary_type)

    def testCP1252(self):
        fh = six.BytesIO(six.b("""OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET: 1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE
"""))
        ofx_file = OfxFile(fh)
        headers = ofx_file.headers
        result = ofx_file.fh.read()

        self.assertTrue(type(result) is six.text_type)
        for key, value in six.iteritems(headers):
            self.assertTrue(type(key) is six.text_type)
            self.assertTrue(type(value) is not six.binary_type)

    def testUTF8Japanese(self):
        fh = six.BytesIO(six.b("""OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:UTF-8
CHARSET:CSUNICODE
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE
"""))
        ofx_file = OfxFile(fh)
        headers = ofx_file.headers
        result = ofx_file.fh.read()

        self.assertTrue(type(result) is six.text_type)
        for key, value in six.iteritems(headers):
            self.assertTrue(type(key) is six.text_type)
            self.assertTrue(type(value) is not six.binary_type)

    def testBrokenLineEndings(self):
        fh = six.BytesIO(six.b("OFXHEADER:100\rDATA:OFXSGML\r"))
        ofx_file = OfxFile(fh)
        self.assertEquals(len(ofx_file.headers.keys()), 2)


class TestParse(TestCase):
    def testEmptyFile(self):
        fh = six.BytesIO(six.b(""))
        self.assertRaises(OfxParserException, OfxParser.parse, fh)

    def testThatParseWorksWithoutErrors(self):
        OfxParser.parse(open_file('bank_medium.ofx'))

    def testThatParseFailsIfNothingToParse(self):
        self.assertRaises(TypeError, OfxParser.parse, None)

    def testThatParseFailsIfAPathIsPassedIn(self):
        # A file handle should be passed in, not the path.
        self.assertRaises(TypeError, OfxParser.parse, '/foo/bar')

    def testThatParseReturnsAResultWithABankAccount(self):
        ofx = OfxParser.parse(open_file('bank_medium.ofx'))
        self.assertTrue(ofx.account is not None)

    def testEverything(self):
        ofx = OfxParser.parse(open_file('bank_medium.ofx'))
        self.assertEquals('12300 000012345678', ofx.account.number)
        self.assertEquals('160000100', ofx.account.routing_number)
        self.assertEquals('00', ofx.account.branch_id)
        self.assertEquals('CHECKING', ofx.account.account_type)
        self.assertEquals(Decimal('382.34'), ofx.account.statement.balance)
        self.assertEquals(datetime(2009, 5, 23, 12, 20, 17),
                          ofx.account.statement.balance_date)
        # Todo: support values in decimal or int form.
        # self.assertEquals('15',
        # ofx.bank_account.statement.balance_in_pennies)
        self.assertEquals(
            Decimal('682.34'), ofx.account.statement.available_balance)
        self.assertEquals(datetime(2009, 5, 23, 12, 20, 17),
                          ofx.account.statement.available_balance_date)
        self.assertEquals(
            datetime(2009, 4, 1), ofx.account.statement.start_date)
        self.assertEquals(
            datetime(2009, 5, 23, 12, 20, 17), ofx.account.statement.end_date)

        self.assertEquals(3, len(ofx.account.statement.transactions))

        transaction = ofx.account.statement.transactions[0]
        self.assertEquals("MCDONALD'S #112", transaction.payee)
        self.assertEquals('pos', transaction.type)
        self.assertEquals(Decimal('-6.60'), transaction.amount)
        # Todo: support values in decimal or int form.
        # self.assertEquals('15', transaction.amount_in_pennies)

    def testMultipleAccounts(self):
        ofx = OfxParser.parse(open_file('multiple_accounts2.ofx'))
        self.assertEquals(2, len(ofx.accounts))
        self.assertEquals('9100', ofx.accounts[0].number)
        self.assertEquals('9200', ofx.accounts[1].number)
        self.assertEquals('123', ofx.accounts[0].routing_number)
        self.assertEquals('123', ofx.accounts[1].routing_number)
        self.assertEquals('CHECKING', ofx.accounts[0].account_type)
        self.assertEquals('SAVINGS', ofx.accounts[1].account_type)


class TestStringToDate(TestCase):
    ''' Test the string to date parser '''
    def test_bad_format(self):
        ''' A poorly formatted string should throw a ValueError '''

        bad_string = 'abcdLOL!'
        self.assertRaises(ValueError, OfxParser.parseOfxDateTime, bad_string)

        bad_but_close_string = '881103'
        self.assertRaises(ValueError, OfxParser.parseOfxDateTime, bad_but_close_string)

        no_month_string = '19881301'
        self.assertRaises(ValueError, OfxParser.parseOfxDateTime, no_month_string)

    def test_returns_none(self):
        self.assertIsNone(OfxParser.parseOfxDateTime('00000000'))

    def test_parses_correct_time(self):
        '''Test whether it can parse correct time for some valid time fields'''
        self.assertEquals(OfxParser.parseOfxDateTime('19881201'),
                          datetime(1988, 12, 1, 0, 0))
        self.assertEquals(OfxParser.parseOfxDateTime('19881201230100'),
                          datetime(1988, 12, 1, 23, 1))
        self.assertEquals(OfxParser.parseOfxDateTime('20120229230100'),
                          datetime(2012, 2, 29, 23, 1))

    def test_parses_time_offset(self):
        ''' Test that we handle GMT offset '''
        self.assertEquals(OfxParser.parseOfxDateTime('20001201120000 [0:GMT]'),
                          datetime(2000, 12, 1, 12, 0))
        self.assertEquals(OfxParser.parseOfxDateTime('19991201120000 [1:ITT]'),
                          datetime(1999, 12, 1, 11, 0))
        self.assertEquals(
            OfxParser.parseOfxDateTime('19881201230100 [-5:EST]'),
            datetime(1988, 12, 2, 4, 1))
        self.assertEquals(
            OfxParser.parseOfxDateTime('20120229230100 [-6:CAT]'),
            datetime(2012, 3, 1, 5, 1))
        self.assertEquals(
            OfxParser.parseOfxDateTime('20120412120000 [-5.5:XXX]'),
            datetime(2012, 4, 12, 17, 30))
        self.assertEquals(
            OfxParser.parseOfxDateTime('20120412120000 [-5:XXX]'),
            datetime(2012, 4, 12, 17))
        self.assertEquals(
            OfxParser.parseOfxDateTime('20120922230000 [+9:JST]'),
            datetime(2012, 9, 22, 14, 0))


class TestParseStmtrs(TestCase):
    input = '''
<STMTRS><CURDEF>CAD<BANKACCTFROM><BANKID>160000100<ACCTID>12300 000012345678<ACCTTYPE>CHECKING</BANKACCTFROM>
<BANKTRANLIST><DTSTART>20090401<DTEND>20090523122017
<STMTTRN><TRNTYPE>POS<DTPOSTED>20090401122017.000[-5:EST]<TRNAMT>-6.60<FITID>0000123456782009040100001<NAME>MCDONALD'S #112<MEMO>POS MERCHANDISE;MCDONALD'S #112</STMTTRN>
</BANKTRANLIST><LEDGERBAL><BALAMT>382.34<DTASOF>20090523122017</LEDGERBAL><AVAILBAL><BALAMT>682.34<DTASOF>20090523122017</AVAILBAL></STMTRS>
    '''

    def testThatParseStmtrsReturnsAnAccount(self):
        stmtrs = soup_maker(self.input)
        account = OfxParser.parseStmtrs(
            stmtrs.find('stmtrs'), AccountType.Bank)[0]
        self.assertEquals('12300 000012345678', account.number)
        self.assertEquals('160000100', account.routing_number)
        self.assertEquals('CHECKING', account.account_type)

    def testThatReturnedAccountAlsoHasAStatement(self):
        stmtrs = soup_maker(self.input)
        account = OfxParser.parseStmtrs(
            stmtrs.find('stmtrs'), AccountType.Bank)[0]
        self.assertTrue(hasattr(account, 'statement'))


class TestAccount(TestCase):
    def testThatANewAccountIsValid(self):
        account = Account()
        self.assertEquals('', account.number)
        self.assertEquals('', account.routing_number)
        self.assertEquals('', account.account_type)
        self.assertEquals(None, account.statement)


class TestParseStatement(TestCase):
    def testThatParseStatementReturnsAStatement(self):
        input = '''
<STMTTRNRS>
 <TRNUID>20090523122017
 <STATUS>
  <CODE>0
  <SEVERITY>INFO
  <MESSAGE>OK
 </STATUS>
 <STMTRS>
  <CURDEF>CAD
  <BANKACCTFROM>
   <BANKID>160000100
   <ACCTID>12300 000012345678
   <ACCTTYPE>CHECKING
  </BANKACCTFROM>
  <BANKTRANLIST>
   <DTSTART>20090401
   <DTEND>20090523122017
   <STMTTRN>
    <TRNTYPE>POS
    <DTPOSTED>20090401122017.000[-5:EST]
    <TRNAMT>-6.60
    <FITID>0000123456782009040100001
    <NAME>MCDONALD'S #112
    <MEMO>POS MERCHANDISE;MCDONALD'S #112
   </STMTTRN>
  </BANKTRANLIST>
  <LEDGERBAL>
   <BALAMT>382.34
   <DTASOF>20090523122017
  </LEDGERBAL>
  <AVAILBAL>
   <BALAMT>682.34
   <DTASOF>20090523122017
  </AVAILBAL>
 </STMTRS>
</STMTTRNRS>
        '''
        txn = soup_maker(input)
        statement = OfxParser.parseStatement(txn.find('stmttrnrs'))
        self.assertEquals(datetime(2009, 4, 1), statement.start_date)
        self.assertEquals(
            datetime(2009, 5, 23, 12, 20, 17), statement.end_date)
        self.assertEquals(1, len(statement.transactions))
        self.assertEquals(Decimal('382.34'), statement.balance)
        self.assertEquals(datetime(2009, 5, 23, 12, 20, 17), statement.balance_date)
        self.assertEquals(Decimal('682.34'), statement.available_balance)
        self.assertEquals(datetime(2009, 5, 23, 12, 20, 17), statement.available_balance_date)

    def testThatParseStatementWithBlankDatesReturnsAStatement(self):
        input = '''
<STMTTRNRS>
 <TRNUID>20090523122017
 <STATUS>
  <CODE>0
  <SEVERITY>INFO
  <MESSAGE>OK
 </STATUS>
 <STMTRS>
  <CURDEF>CAD
  <BANKACCTFROM>
   <BANKID>160000100
   <ACCTID>12300 000012345678
   <ACCTTYPE>CHECKING
  </BANKACCTFROM>
  <BANKTRANLIST>
   <DTSTART>00000000
   <DTEND>00000000
   <STMTTRN>
    <TRNTYPE>POS
    <DTPOSTED>20090401122017.000[-5:EST]
    <TRNAMT>-6.60
    <FITID>0000123456782009040100001
    <NAME>MCDONALD'S #112
    <MEMO>POS MERCHANDISE;MCDONALD'S #112
   </STMTTRN>
  </BANKTRANLIST>
  <LEDGERBAL>
   <BALAMT>382.34
   <DTASOF>20090523122017
  </LEDGERBAL>
  <AVAILBAL>
   <BALAMT>682.34
   <DTASOF>20090523122017
  </AVAILBAL>
 </STMTRS>
</STMTTRNRS>
        '''
        txn = soup_maker(input)
        statement = OfxParser.parseStatement(txn.find('stmttrnrs'))
        self.assertEquals(None, statement.start_date)
        self.assertEquals(None, statement.end_date)
        self.assertEquals(1, len(statement.transactions))
        self.assertEquals(Decimal('382.34'), statement.balance)
        self.assertEquals(datetime(2009, 5, 23, 12, 20, 17), statement.balance_date)
        self.assertEquals(Decimal('682.34'), statement.available_balance)
        self.assertEquals(datetime(2009, 5, 23, 12, 20, 17), statement.available_balance_date)

class TestStatement(TestCase):
    def testThatANewStatementIsValid(self):
        statement = Statement()
        self.assertEquals('', statement.start_date)
        self.assertEquals('', statement.end_date)
        self.assertEquals(0, len(statement.transactions))


class TestParseTransaction(TestCase):
    def testThatParseTransactionReturnsATransaction(self):
        input = '''
<STMTTRN>
 <TRNTYPE>POS
 <DTPOSTED>20090401122017.000[-5:EST]
 <TRNAMT>-6.60
 <FITID>0000123456782009040100001
 <NAME>MCDONALD'S #112
 <MEMO>POS MERCHANDISE;MCDONALD'S #112
</STMTTRN>
'''
        txn = soup_maker(input)
        transaction = OfxParser.parseTransaction(txn.find('stmttrn'))
        self.assertEquals('pos', transaction.type)
        self.assertEquals(datetime(
            2009, 4, 1, 12, 20, 17) - timedelta(hours=-5), transaction.date)
        self.assertEquals(Decimal('-6.60'), transaction.amount)
        self.assertEquals('0000123456782009040100001', transaction.id)
        self.assertEquals("MCDONALD'S #112", transaction.payee)
        self.assertEquals("POS MERCHANDISE;MCDONALD'S #112", transaction.memo)

    def testThatParseTransactionWithFieldCheckNum(self):
        input = '''
<STMTTRN>
 <TRNTYPE>DEP
 <DTPOSTED>20130306
 <TRNAMT>1000.00
 <FITID>2013030601009100
 <CHECKNUM>700
 <MEMO>DEPOSITO ONLINE
</STMTTRN>
'''
        txn = soup_maker(input)
        transaction = OfxParser.parseTransaction(txn.find('stmttrn'))
        self.assertEquals('700', transaction.checknum)

    def testThatParseTransactionWithCommaAsDecimalPoint(self):
        input = '''
<STMTTRN>
 <TRNTYPE>POS
 <DTPOSTED>20090401122017.000[-5:EST]
 <TRNAMT>-1006,60
 <FITID>0000123456782009040100001
 <NAME>MCDONALD'S #112
 <MEMO>POS MERCHANDISE;MCDONALD'S #112
</STMTTRN>
'''
        txn = soup_maker(input)
        transaction = OfxParser.parseTransaction(txn.find('stmttrn'))
        self.assertEquals(Decimal('-1006.60'), transaction.amount)

    def testThatParseTransactionWithCommaAsDecimalPointAndDotAsSeparator(self):
        input = '''
<STMTTRN>
 <TRNTYPE>POS
 <DTPOSTED>20090401122017.000[-5:EST]
 <TRNAMT>-1.006,60
 <FITID>0000123456782009040100001
 <NAME>MCDONALD'S #112
 <MEMO>POS MERCHANDISE;MCDONALD'S #112
</STMTTRN>
'''
        txn = soup_maker(input)
        with self.assertRaises(OfxParserException):
            transaction = OfxParser.parseTransaction(txn.find('stmttrn'))

    def testThatParseTransactionWithNullAmountIgnored(self):
        """A null transaction value is converted to 0.

        Some banks use a null transaction to include interest
        rate changes on statements.
        """
        input_template = '''
<STMTTRN>
 <TRNTYPE>DEP
 <DTPOSTED>20130306
 <TRNAMT>{amount}
 <FITID>2013030601009100
 <CHECKNUM>700
 <MEMO>DEPOSITO ONLINE
</STMTTRN>
'''
        for amount in ("null", "-null"):
            input = input_template.format(amount=amount)
            txn = soup_maker(input)

            transaction = OfxParser.parseTransaction(txn.find('stmttrn'))

            self.assertEquals(0, transaction.amount)


class TestTransaction(TestCase):
    def testThatAnEmptyTransactionIsValid(self):
        t = Transaction()
        self.assertEquals('', t.payee)
        self.assertEquals('', t.type)
        self.assertEquals(None, t.date)
        self.assertEquals(None, t.amount)
        self.assertEquals('', t.id)
        self.assertEquals('', t.memo)
        self.assertEquals('', t.checknum)


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
        OfxParser.parse(six.BytesIO(six.b(self.sample)))
        # Success!


class TestVanguardInvestmentStatement(TestCase):
    def testForUnclosedTags(self):
        ofx = OfxParser.parse(open_file('vanguard.ofx'))
        self.assertTrue(hasattr(ofx, 'account'))
        self.assertTrue(hasattr(ofx.account, 'statement'))
        self.assertTrue(hasattr(ofx.account.statement, 'transactions'))
        self.assertEquals(len(ofx.account.statement.transactions), 1)
        self.assertEquals(ofx.account.statement.transactions[0].id,
                          '01234567890.0123.07152011.0')
        self.assertEquals(ofx.account.statement.transactions[0]
                          .tradeDate, datetime(2011, 7, 15, 21))
        self.assertEquals(ofx.account.statement.transactions[0]
                          .settleDate, datetime(2011, 7, 15, 21))
        self.assertTrue(hasattr(ofx.account.statement, 'positions'))
        self.assertEquals(len(ofx.account.statement.positions), 2)
        self.assertEquals(
            ofx.account.statement.positions[0].units, Decimal('102.0'))

    def testSecurityListSuccess(self):
        ofx = OfxParser.parse(open_file('vanguard.ofx'))
        self.assertEquals(len(ofx.security_list), 2)


class TestVanguard401kStatement(TestCase):
    def testReadTransfer(self):
        ofx = OfxParser.parse(open_file('vanguard401k.ofx'))
        self.assertTrue(hasattr(ofx, 'account'))
        self.assertTrue(hasattr(ofx.account, 'statement'))
        self.assertTrue(hasattr(ofx.account.statement, 'transactions'))
        self.assertEquals(len(ofx.account.statement.transactions), 5)
        self.assertEquals(ofx.account.statement.transactions[-1].id,
                          '1234567890123456795AAA')
        self.assertEquals('transfer', ofx.account.statement.transactions[-1].type)
        self.assertEquals(ofx.account.statement.transactions[-1].inv401ksource,
                          'MATCH')


class TestFidelityInvestmentStatement(TestCase):
    def testForUnclosedTags(self):
        ofx = OfxParser.parse(open_file('fidelity.ofx'))
        self.assertTrue(hasattr(ofx.account.statement, 'positions'))
        self.assertEquals(len(ofx.account.statement.positions), 6)
        self.assertEquals(
            ofx.account.statement.positions[0].units, Decimal('128.0'))

    def testSecurityListSuccess(self):
        ofx = OfxParser.parse(open_file('fidelity.ofx'))
        self.assertEquals(len(ofx.security_list), 7)


class Test401InvestmentStatement(TestCase):
    def testTransferAggregate(self):
        ofx = OfxParser.parse(open_file('investment_401k.ofx'))
        expected_txns = [{'id': '1',
                          'type': 'buymf',
                          'units': Decimal('8.846699'),
                          'unit_price': Decimal('22.2908'),
                          'total': Decimal('-197.2'),
                          'security': 'FOO'},
                         {'id': '2',
                          'type': 'transfer',
                          'units': Decimal('6.800992'),
                          'unit_price': Decimal('29.214856'),
                          'total': Decimal('0.0'),
                          'security': 'BAR'},
                         {'id': '3',
                          'type': 'transfer',
                          'units': Decimal('-9.060702'),
                          'unit_price': Decimal('21.928764'),
                          'total': Decimal('0.0'),
                          'security': 'BAZ'}]
        for txn, expected_txn in zip(ofx.account.statement.transactions, expected_txns):
            self.assertEquals(txn.id, expected_txn['id'])
            self.assertEquals(txn.type, expected_txn['type'])
            self.assertEquals(txn.units, expected_txn['units'])
            self.assertEquals(txn.unit_price, expected_txn['unit_price'])
            self.assertEquals(txn.total, expected_txn['total'])
            self.assertEquals(txn.security, expected_txn['security'])

        expected_positions = [{'security': 'FOO',
                               'units': Decimal('17.604312'),
                               'unit_price': Decimal('22.517211')},
                              {'security': 'BAR',
                               'units': Decimal('13.550983'),
                               'unit_price': Decimal('29.214855')},
                              {'security': 'BAZ',
                               'units': Decimal('0.0'),
                               'unit_price': Decimal('0.0')}]
        for pos, expected_pos in zip(ofx.account.statement.positions, expected_positions):
            self.assertEquals(pos.security, expected_pos['security'])
            self.assertEquals(pos.units, expected_pos['units'])
            self.assertEquals(pos.unit_price, expected_pos['unit_price'])


class TestSuncorpBankStatement(TestCase):
    def testCDATATransactions(self):
        ofx = OfxParser.parse(open_file('suncorp.ofx'))
        accounts = ofx.accounts
        self.assertEquals(len(accounts), 1)
        account = accounts[0]
        transactions = account.statement.transactions
        self.assertEquals(len(transactions), 1)
        transaction = transactions[0]
        self.assertEquals(transaction.payee, "EFTPOS WDL HANDYWAY ALDI STORE")
        self.assertEquals(
            transaction.memo,
            "EFTPOS WDL HANDYWAY ALDI STORE   GEELONG WEST VICAU")
        self.assertEquals(transaction.amount, Decimal("-16.85"))


class TestAccountInfoAggregation(TestCase):
    def testForFourAccounts(self):
        ofx = OfxParser.parse(open_file('account_listing_aggregation.ofx'))
        self.assertTrue(hasattr(ofx, 'accounts'))
        self.assertEquals(len(ofx.accounts), 4)

        # first account
        account = ofx.accounts[0]
        self.assertEquals(account.account_type, 'SAVINGS')
        self.assertEquals(account.desc, 'USAA SAVINGS')
        self.assertEquals(account.institution.organization, 'USAA')
        self.assertEquals(account.number, '0000000001')
        self.assertEquals(account.routing_number, '314074269')

        # second
        account = ofx.accounts[1]
        self.assertEquals(account.account_type, 'CHECKING')
        self.assertEquals(account.desc, 'FOUR STAR CHECKING')
        self.assertEquals(account.institution.organization, 'USAA')
        self.assertEquals(account.number, '0000000002')
        self.assertEquals(account.routing_number, '314074269')

        # third
        account = ofx.accounts[2]
        self.assertEquals(account.account_type, 'CREDITLINE')
        self.assertEquals(account.desc, 'LINE OF CREDIT')
        self.assertEquals(account.institution.organization, 'USAA')
        self.assertEquals(account.number, '00000000000003')
        self.assertEquals(account.routing_number, '314074269')

        # fourth
        account = ofx.accounts[3]
        self.assertEquals(account.account_type, '')
        self.assertEquals(account.desc, 'MY CREDIT CARD')
        self.assertEquals(account.institution.organization, 'USAA')
        self.assertEquals(account.number, '4111111111111111')


class TestGracefulFailures(TestCase):
    ''' Test that when fail_fast is False, failures are returned to the
    caller as warnings and discarded entries in the Statement class.
    '''
    def testDateFieldMissing(self):
        ''' The test file contains three transactions in a single
        statement.

        They fail due to:
        1) No date
        2) Empty date
        3) Invalid date
        '''
        ofx = OfxParser.parse(open_file('fail_nice/date_missing.ofx'), False)
        self.assertEquals(len(ofx.account.statement.transactions), 0)
        self.assertEquals(len(ofx.account.statement.discarded_entries), 3)
        self.assertEquals(len(ofx.account.statement.warnings), 0)

        # Test that it raises an error otherwise.
        self.assertRaises(OfxParserException, OfxParser.parse,
                          open_file('fail_nice/date_missing.ofx'))

    def testDecimalConversionError(self):
        ''' The test file contains a transaction that has a poorly formatted
        decimal number ($20). Test that we catch this.
        '''
        ofx = OfxParser.parse(open_file('fail_nice/decimal_error.ofx'), False)
        self.assertEquals(len(ofx.account.statement.transactions), 0)
        self.assertEquals(len(ofx.account.statement.discarded_entries), 1)

        # Test that it raises an error otherwise.
        self.assertRaises(OfxParserException, OfxParser.parse,
                          open_file('fail_nice/decimal_error.ofx'))

    def testEmptyBalance(self):
        ''' The test file contains empty or blank strings in the balance
        fields. Fail nicely on those.
        '''
        ofx = OfxParser.parse(open_file('fail_nice/empty_balance.ofx'), False)
        self.assertEquals(len(ofx.account.statement.transactions), 1)
        self.assertEquals(len(ofx.account.statement.discarded_entries), 0)
        self.assertFalse(hasattr(ofx.account.statement, 'balance'))
        self.assertFalse(hasattr(ofx.account.statement, 'available_balance'))

        # Test that it raises an error otherwise.
        self.assertRaises(OfxParserException, OfxParser.parse,
                          open_file('fail_nice/empty_balance.ofx'))


class TestParseSonrs(TestCase):

    def testSuccess(self):
        ofx = OfxParser.parse(open_file('signon_success.ofx'), True)
        self.assertTrue(ofx.signon.success)
        self.assertEquals(ofx.signon.code, 0)
        self.assertEquals(ofx.signon.severity, 'INFO')
        self.assertEquals(ofx.signon.message, 'Login successful')

        ofx = OfxParser.parse(open_file('signon_success_no_message.ofx'), True)
        self.assertTrue(ofx.signon.success)
        self.assertEquals(ofx.signon.code, 0)
        self.assertEquals(ofx.signon.severity, 'INFO')
        self.assertEquals(ofx.signon.message, '')

    def testFailure(self):
        ofx = OfxParser.parse(open_file('signon_fail.ofx'), True)
        self.assertFalse(ofx.signon.success)
        self.assertEquals(ofx.signon.code, 15500)
        self.assertEquals(ofx.signon.severity, 'ERROR')
        self.assertEquals(ofx.signon.message, 'Your request could not be processed because you supplied an invalid identification code or your password was incorrect')

if __name__ == "__main__":
    import unittest
    unittest.main()
