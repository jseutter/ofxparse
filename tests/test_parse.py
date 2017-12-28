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


class TestOfxFile(TestCase):
    OfxFileCls = OfxFile

    def assertHeadersTypes(self, headers):
        """
        Assert that the headers keys and values have the correct types

        :param headers: headers dict from a OfxFile or OfxPreprocessedFile instance
        """
        for key, value in six.iteritems(headers):
            self.assertTrue(type(key) is six.text_type)
            self.assertTrue(type(value) is not six.binary_type)

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
        with open_file('bank_medium.ofx') as f:
            ofx = OfxParser.parse(f)
        self.assertEqual(expect, ofx.headers)

    def testTextFileHandler(self):
        with open_file("bank_medium.ofx") as fh:
            with open_file("bank_medium.ofx", mode="r") as fh_str:
                ofx_file = self.OfxFileCls(fh)
                headers = ofx_file.headers
                data = ofx_file.fh.read()

                self.assertTrue(type(data) is six.text_type)
                self.assertHeadersTypes(headers)

                ofx_file = self.OfxFileCls(fh_str)
                headers = ofx_file.headers
                data = ofx_file.fh.read()

                self.assertTrue(type(data) is six.text_type)
                self.assertHeadersTypes(headers)

    def testTextStartsWithTag(self):
        with open_file('anzcc.ofx', mode='r') as f:
            ofx = OfxParser.parse(f)
        self.assertEqual(ofx.account.number, '1234123412341234')

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
        ofx_file = self.OfxFileCls(fh)
        headers = ofx_file.headers
        data = ofx_file.fh.read()

        self.assertTrue(type(data) is six.text_type)
        self.assertHeadersTypes(headers)

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
        ofx_file = self.OfxFileCls(fh)
        headers = ofx_file.headers
        result = ofx_file.fh.read()

        self.assertTrue(type(result) is six.text_type)
        self.assertHeadersTypes(headers)

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
        ofx_file = self.OfxFileCls(fh)
        headers = ofx_file.headers
        result = ofx_file.fh.read()

        self.assertTrue(type(result) is six.text_type)
        self.assertHeadersTypes(headers)

    def testBrokenLineEndings(self):
        fh = six.BytesIO(six.b("OFXHEADER:100\rDATA:OFXSGML\r"))
        ofx_file = self.OfxFileCls(fh)
        self.assertEqual(len(ofx_file.headers.keys()), 2)


class TestOfxPreprocessedFile(TestOfxFile):
    OfxFileCls = OfxPreprocessedFile

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


class TestParse(TestCase):
    def testEmptyFile(self):
        fh = six.BytesIO(six.b(""))
        self.assertRaises(OfxParserException, OfxParser.parse, fh)

    def testThatParseWorksWithoutErrors(self):
        with open_file('bank_medium.ofx') as f:
            OfxParser.parse(f)

    def testThatParseFailsIfNothingToParse(self):
        self.assertRaises(TypeError, OfxParser.parse, None)

    def testThatParseFailsIfAPathIsPassedIn(self):
        # A file handle should be passed in, not the path.
        self.assertRaises(TypeError, OfxParser.parse, '/foo/bar')

    def testThatParseReturnsAResultWithABankAccount(self):
        with open_file('bank_medium.ofx') as f:
            ofx = OfxParser.parse(f)
        self.assertTrue(ofx.account is not None)

    def testEverything(self):
        with open_file('bank_medium.ofx') as f:
            ofx = OfxParser.parse(f)
        self.assertEqual('12300 000012345678', ofx.account.number)
        self.assertEqual('160000100', ofx.account.routing_number)
        self.assertEqual('00', ofx.account.branch_id)
        self.assertEqual('CHECKING', ofx.account.account_type)
        self.assertEqual(Decimal('382.34'), ofx.account.statement.balance)
        self.assertEqual(datetime(2009, 5, 23, 12, 20, 17),
                          ofx.account.statement.balance_date)
        # Todo: support values in decimal or int form.
        # self.assertEqual('15',
        # ofx.bank_account.statement.balance_in_pennies)
        self.assertEqual(
            Decimal('682.34'), ofx.account.statement.available_balance)
        self.assertEqual(datetime(2009, 5, 23, 12, 20, 17),
                          ofx.account.statement.available_balance_date)
        self.assertEqual(
            datetime(2009, 4, 1), ofx.account.statement.start_date)
        self.assertEqual(
            datetime(2009, 5, 23, 12, 20, 17), ofx.account.statement.end_date)

        self.assertEqual(3, len(ofx.account.statement.transactions))

        transaction = ofx.account.statement.transactions[0]
        self.assertEqual("MCDONALD'S #112", transaction.payee)
        self.assertEqual('pos', transaction.type)
        self.assertEqual(Decimal('-6.60'), transaction.amount)
        # Todo: support values in decimal or int form.
        # self.assertEqual('15', transaction.amount_in_pennies)

    def testMultipleAccounts(self):
        with open_file('multiple_accounts2.ofx') as f:
            ofx = OfxParser.parse(f)
        self.assertEqual(2, len(ofx.accounts))
        self.assertEqual('9100', ofx.accounts[0].number)
        self.assertEqual('9200', ofx.accounts[1].number)
        self.assertEqual('123', ofx.accounts[0].routing_number)
        self.assertEqual('123', ofx.accounts[1].routing_number)
        self.assertEqual('CHECKING', ofx.accounts[0].account_type)
        self.assertEqual('SAVINGS', ofx.accounts[1].account_type)


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
        self.assertEqual(OfxParser.parseOfxDateTime('19881201'),
                          datetime(1988, 12, 1, 0, 0))
        self.assertEqual(OfxParser.parseOfxDateTime('19881201230100'),
                          datetime(1988, 12, 1, 23, 1))
        self.assertEqual(OfxParser.parseOfxDateTime('20120229230100'),
                          datetime(2012, 2, 29, 23, 1))

    def test_parses_time_offset(self):
        ''' Test that we handle GMT offset '''
        self.assertEqual(OfxParser.parseOfxDateTime('20001201120000 [0:GMT]'),
                          datetime(2000, 12, 1, 12, 0))
        self.assertEqual(OfxParser.parseOfxDateTime('19991201120000 [1:ITT]'),
                          datetime(1999, 12, 1, 11, 0))
        self.assertEqual(
            OfxParser.parseOfxDateTime('19881201230100 [-5:EST]'),
            datetime(1988, 12, 2, 4, 1))
        self.assertEqual(
            OfxParser.parseOfxDateTime('20120229230100 [-6:CAT]'),
            datetime(2012, 3, 1, 5, 1))
        self.assertEqual(
            OfxParser.parseOfxDateTime('20120412120000 [-5.5:XXX]'),
            datetime(2012, 4, 12, 17, 30))
        self.assertEqual(
            OfxParser.parseOfxDateTime('20120412120000 [-5:XXX]'),
            datetime(2012, 4, 12, 17))
        self.assertEqual(
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
        self.assertEqual('12300 000012345678', account.number)
        self.assertEqual('160000100', account.routing_number)
        self.assertEqual('CHECKING', account.account_type)

    def testThatReturnedAccountAlsoHasAStatement(self):
        stmtrs = soup_maker(self.input)
        account = OfxParser.parseStmtrs(
            stmtrs.find('stmtrs'), AccountType.Bank)[0]
        self.assertTrue(hasattr(account, 'statement'))


class TestAccount(TestCase):
    def testThatANewAccountIsValid(self):
        account = Account()
        self.assertEqual('', account.number)
        self.assertEqual('', account.routing_number)
        self.assertEqual('', account.account_type)
        self.assertEqual(None, account.statement)


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
        self.assertEqual(datetime(2009, 4, 1), statement.start_date)
        self.assertEqual(
            datetime(2009, 5, 23, 12, 20, 17), statement.end_date)
        self.assertEqual(1, len(statement.transactions))
        self.assertEqual(Decimal('382.34'), statement.balance)
        self.assertEqual(datetime(2009, 5, 23, 12, 20, 17), statement.balance_date)
        self.assertEqual(Decimal('682.34'), statement.available_balance)
        self.assertEqual(datetime(2009, 5, 23, 12, 20, 17), statement.available_balance_date)

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
        self.assertEqual(None, statement.start_date)
        self.assertEqual(None, statement.end_date)
        self.assertEqual(1, len(statement.transactions))
        self.assertEqual(Decimal('382.34'), statement.balance)
        self.assertEqual(datetime(2009, 5, 23, 12, 20, 17), statement.balance_date)
        self.assertEqual(Decimal('682.34'), statement.available_balance)
        self.assertEqual(datetime(2009, 5, 23, 12, 20, 17), statement.available_balance_date)

class TestStatement(TestCase):
    def testThatANewStatementIsValid(self):
        statement = Statement()
        self.assertEqual('', statement.start_date)
        self.assertEqual('', statement.end_date)
        self.assertEqual(0, len(statement.transactions))


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
        self.assertEqual('pos', transaction.type)
        self.assertEqual(datetime(
            2009, 4, 1, 12, 20, 17) - timedelta(hours=-5), transaction.date)
        self.assertEqual(Decimal('-6.60'), transaction.amount)
        self.assertEqual('0000123456782009040100001', transaction.id)
        self.assertEqual("MCDONALD'S #112", transaction.payee)
        self.assertEqual("POS MERCHANDISE;MCDONALD'S #112", transaction.memo)

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
        self.assertEqual('700', transaction.checknum)

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
        self.assertEqual(Decimal('-1006.60'), transaction.amount)

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
        transaction = OfxParser.parseTransaction(txn.find('stmttrn'))
        self.assertEqual(Decimal('-1006.60'), transaction.amount)

    def testThatParseTransactionWithDotAsDecimalPointAndCommaAsSeparator(self):
        " The exact opposite of the previous test.  Why are numbers so hard?"
        input = '''
<STMTTRN>
 <TRNTYPE>POS
 <DTPOSTED>20090401122017.000[-5:EST]
 <TRNAMT>-1,006.60
 <FITID>0000123456782009040100001
 <NAME>MCDONALD'S #112
 <MEMO>POS MERCHANDISE;MCDONALD'S #112
</STMTTRN>
'''
        txn = soup_maker(input)
        transaction = OfxParser.parseTransaction(txn.find('stmttrn'))
        self.assertEqual(Decimal('-1006.60'), transaction.amount)

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

            self.assertEqual(0, transaction.amount)


class TestTransaction(TestCase):
    def testThatAnEmptyTransactionIsValid(self):
        t = Transaction()
        self.assertEqual('', t.payee)
        self.assertEqual('', t.type)
        self.assertEqual(None, t.date)
        self.assertEqual(None, t.amount)
        self.assertEqual('', t.id)
        self.assertEqual('', t.memo)
        self.assertEqual('', t.checknum)


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
        with open_file('vanguard.ofx') as f:
            ofx = OfxParser.parse(f)
        self.assertTrue(hasattr(ofx, 'account'))
        self.assertTrue(hasattr(ofx.account, 'statement'))
        self.assertTrue(hasattr(ofx.account.statement, 'transactions'))
        self.assertEqual(len(ofx.account.statement.transactions), 1)
        self.assertEqual(ofx.account.statement.transactions[0].id,
                          '01234567890.0123.07152011.0')
        self.assertEqual(ofx.account.statement.transactions[0]
                          .tradeDate, datetime(2011, 7, 15, 21))
        self.assertEqual(ofx.account.statement.transactions[0]
                          .settleDate, datetime(2011, 7, 15, 21))
        self.assertTrue(hasattr(ofx.account.statement, 'positions'))
        self.assertEqual(len(ofx.account.statement.positions), 2)
        self.assertEqual(
            ofx.account.statement.positions[0].units, Decimal('102.0'))

    def testSecurityListSuccess(self):
        with open_file('vanguard.ofx') as f:
            ofx = OfxParser.parse(f)
        self.assertEqual(len(ofx.security_list), 2)


class TestVanguard401kStatement(TestCase):
    def testReadTransfer(self):
        with open_file('vanguard401k.ofx') as f:
            ofx = OfxParser.parse(f)
        self.assertTrue(hasattr(ofx, 'account'))
        self.assertTrue(hasattr(ofx.account, 'statement'))
        self.assertTrue(hasattr(ofx.account.statement, 'transactions'))
        self.assertEqual(len(ofx.account.statement.transactions), 5)
        self.assertEqual(ofx.account.statement.transactions[-1].id,
                          '1234567890123456795AAA')
        self.assertEqual('transfer', ofx.account.statement.transactions[-1].type)
        self.assertEqual(ofx.account.statement.transactions[-1].inv401ksource,
                          'MATCH')


class TestTiaaCrefStatement(TestCase):
    def testReadAccount(self):
        with open_file('tiaacref.ofx') as f:
            ofx = OfxParser.parse(f)
        self.assertTrue(hasattr(ofx, 'account'))
        self.assertTrue(hasattr(ofx.account, 'account_id'))
        self.assertEqual(ofx.account.account_id, '111A1111 22B222 33C333')
        self.assertTrue(hasattr(ofx.account, 'type'))
        self.assertEqual(ofx.account.type, AccountType.Investment)

    def testReadTransfer(self):
        with open_file('tiaacref.ofx') as f:
            ofx = OfxParser.parse(f)
        self.assertTrue(hasattr(ofx, 'account'))
        self.assertTrue(hasattr(ofx.account, 'statement'))
        self.assertTrue(hasattr(ofx.account.statement, 'transactions'))
        self.assertEqual(len(ofx.account.statement.transactions), 1)
        self.assertEqual(
            ofx.account.statement.transactions[-1].id,
            'TIAA#20170307160000.000[-4:EDT]160000.000[-4:EDT]'
        )
        self.assertEqual(
            'transfer',
            ofx.account.statement.transactions[-1].type
        )

    def testReadPositions(self):
        with open_file('tiaacref.ofx') as f:
            ofx = OfxParser.parse(f)
        self.assertTrue(hasattr(ofx, 'account'))
        self.assertTrue(hasattr(ofx.account, 'statement'))
        self.assertTrue(hasattr(ofx.account.statement, 'positions'))
        expected_positions = [
            {
                'security': '222222126',
                'units': Decimal('13.0763'),
                'unit_price': Decimal('1.0000'),
                'market_value': Decimal('13.0763')
            },
            {
                'security': '222222217',
                'units': Decimal('1.0000'),
                'unit_price': Decimal('25.5785'),
                'market_value': Decimal('25.5785')
            },
            {
                'security': '222222233',
                'units': Decimal('8.7605'),
                'unit_price': Decimal('12.4823'),
                'market_value': Decimal('109.3512')
            },
            {
                'security': '222222258',
                'units': Decimal('339.2012'),
                'unit_price': Decimal('12.3456'),
                'market_value': Decimal('4187.6423')
            },
            {
                'security': '111111111',
                'units': Decimal('543.71'),
                'unit_price': Decimal('1'),
                'market_value': Decimal('543.71')
            },
            {
                'security': '333333200',
                'units': Decimal('2.00'),
                'unit_price': Decimal('10.00'),
                'market_value': Decimal('20.00')
            }
        ]
        self.assertEqual(
            len(ofx.account.statement.positions),
            len(expected_positions)
        )
        for pos, expected_pos in zip(
                ofx.account.statement.positions, expected_positions
        ):
            self.assertEqual(pos.security, expected_pos['security'])
            self.assertEqual(pos.units, expected_pos['units'])
            self.assertEqual(pos.unit_price, expected_pos['unit_price'])
            self.assertEqual(pos.market_value, expected_pos['market_value'])


class TestFidelityInvestmentStatement(TestCase):
    def testForUnclosedTags(self):
        with open_file('fidelity.ofx') as f:
            ofx = OfxParser.parse(f)
        self.assertTrue(hasattr(ofx.account.statement, 'positions'))
        self.assertEqual(len(ofx.account.statement.positions), 6)
        self.assertEqual(
            ofx.account.statement.positions[0].units, Decimal('128.0'))
        self.assertEqual(
            ofx.account.statement.positions[0].market_value, Decimal('5231.36')
        )

    def testSecurityListSuccess(self):
        with open_file('fidelity.ofx') as f:
            ofx = OfxParser.parse(f)
        self.assertEqual(len(ofx.security_list), 7)

    def testBalanceList(self):
        with open_file('fidelity.ofx') as f:
            ofx = OfxParser.parse(f)
        self.assertEqual(len(ofx.account.statement.balance_list), 18)
        self.assertEqual(ofx.account.statement.balance_list[0].name, 'Networth')
        self.assertEqual(ofx.account.statement.balance_list[0].description, 'The net market value of all long and short positions in the account')
        self.assertEqual(ofx.account.statement.balance_list[0].value, Decimal('32993.79'))
        self.assertEqual(ofx.account.statement.available_cash, Decimal('18073.98'))
        self.assertEqual(ofx.account.statement.margin_balance, Decimal('0'))
        self.assertEqual(ofx.account.statement.short_balance, Decimal('0'))
        self.assertEqual(ofx.account.statement.buy_power, Decimal('0'))

class TestFidelitySavingsStatement(TestCase):
    def testSTMTTRNInInvestmentBank(self):
        with open_file('fidelity-savings.ofx') as f:
            ofx = OfxParser.parse(f)

        self.assertTrue(hasattr(ofx.account.statement, 'transactions'))
        self.assertEqual(len(ofx.account.statement.transactions), 4)

        tx = ofx.account.statement.transactions[0]
        self.assertEqual('check', tx.type)
        self.assertEqual(datetime(
            2012, 7, 20, 0, 0, 0) - timedelta(hours=-4), tx.date)
        self.assertEqual(Decimal('-1500.00'), tx.amount)
        self.assertEqual('X0000000000000000000001', tx.id)
        self.assertEqual('Check Paid #0000001001', tx.payee)
        self.assertEqual('Check Paid #0000001001', tx.memo)

        tx = ofx.account.statement.transactions[1]
        self.assertEqual('dep', tx.type)
        self.assertEqual(datetime(
            2012, 7, 27, 0, 0, 0) - timedelta(hours=-4), tx.date)
        self.assertEqual(Decimal('115.8331'), tx.amount)
        self.assertEqual('X0000000000000000000002', tx.id)
        self.assertEqual('TRANSFERRED FROM     VS X10-08144', tx.payee)
        self.assertEqual('TRANSFERRED FROM     VS X10-08144-1', tx.memo)

class Test401InvestmentStatement(TestCase):
    def testTransferAggregate(self):
        with open_file('investment_401k.ofx') as f:
            ofx = OfxParser.parse(f)
        expected_txns = [{'id': '1',
                          'type': 'buymf',
                          'units': Decimal('8.846699'),
                          'unit_price': Decimal('22.2908'),
                          'total': Decimal('-197.2'),
                          'security': 'FOO',
                          'tferaction': None},
                         {'id': '2',
                          'type': 'transfer',
                          'units': Decimal('6.800992'),
                          'unit_price': Decimal('29.214856'),
                          'total': Decimal('0.0'),
                          'security': 'BAR',
                          'tferaction': 'IN'},
                         {'id': '3',
                          'type': 'transfer',
                          'units': Decimal('-9.060702'),
                          'unit_price': Decimal('21.928764'),
                          'total': Decimal('0.0'),
                          'security': 'BAZ',
                          'tferaction': 'OUT'}]
        for txn, expected_txn in zip(ofx.account.statement.transactions, expected_txns):
            self.assertEqual(txn.id, expected_txn['id'])
            self.assertEqual(txn.type, expected_txn['type'])
            self.assertEqual(txn.units, expected_txn['units'])
            self.assertEqual(txn.unit_price, expected_txn['unit_price'])
            self.assertEqual(txn.total, expected_txn['total'])
            self.assertEqual(txn.security, expected_txn['security'])
            self.assertEqual(txn.tferaction, expected_txn['tferaction'])

        expected_positions = [
            {
                'security': 'FOO',
                'units': Decimal('17.604312'),
                'unit_price': Decimal('22.517211'),
                'market_value': Decimal('396.4')
            },
            {
                'security': 'BAR',
                'units': Decimal('13.550983'),
                'unit_price': Decimal('29.214855'),
                'market_value': Decimal('395.89')
            },
            {
                'security': 'BAZ',
                'units': Decimal('0.0'),
                'unit_price': Decimal('0.0'),
                'market_value': Decimal('0.0')
            }
        ]
        for pos, expected_pos in zip(ofx.account.statement.positions, expected_positions):
            self.assertEqual(pos.security, expected_pos['security'])
            self.assertEqual(pos.units, expected_pos['units'])
            self.assertEqual(pos.unit_price, expected_pos['unit_price'])
            self.assertEqual(pos.market_value, expected_pos['market_value'])


class TestSuncorpBankStatement(TestCase):
    def testCDATATransactions(self):
        with open_file('suncorp.ofx') as f:
            ofx = OfxParser.parse(f)
        accounts = ofx.accounts
        self.assertEqual(len(accounts), 1)
        account = accounts[0]
        transactions = account.statement.transactions
        self.assertEqual(len(transactions), 1)
        transaction = transactions[0]
        self.assertEqual(transaction.payee, "EFTPOS WDL HANDYWAY ALDI STORE")
        self.assertEqual(
            transaction.memo,
            "EFTPOS WDL HANDYWAY ALDI STORE   GEELONG WEST VICAU")
        self.assertEqual(transaction.amount, Decimal("-16.85"))

class TestTDAmeritrade(TestCase):
    def testPositions(self):
        with open_file('td_ameritrade.ofx') as f:
            ofx = OfxParser.parse(f)
        account = ofx.accounts[0]
        statement = account.statement
        positions = statement.positions
        self.assertEquals(len(positions), 2)

        expected_positions = [
            {
                'security': '023135106',
                'units': Decimal('1'),
                'unit_price': Decimal('1000'),
                'market_value': Decimal('1000')
            },
            {
                'security': '912810RW0',
                'units': Decimal('1000'),
                'unit_price': Decimal('100'),
                'market_value': Decimal('1000')
            }
        ]
        for pos, expected_pos in zip(positions, expected_positions):
            self.assertEqual(pos.security, expected_pos['security'])
            self.assertEqual(pos.units, expected_pos['units'])
            self.assertEqual(pos.unit_price, expected_pos['unit_price'])
            self.assertEqual(pos.market_value, expected_pos['market_value'])

        expected_securities = [
            {
                'uniqueid': '023135106',
                'ticker': 'AMZN',
                'name': 'Amazon.com, Inc. - Common Stock'
            },
            {
                'uniqueid': '912810RW0',
                'ticker': '912810RW0',
                'name': 'US Treasury 2047'
            }
        ]
        for sec, expected_sec in zip(ofx.security_list, expected_securities):
            self.assertEqual(sec.uniqueid, expected_sec['uniqueid'])
            self.assertEqual(sec.ticker, expected_sec['ticker'])
            self.assertEqual(sec.name, expected_sec['name'])

class TestAccountInfoAggregation(TestCase):
    def testForFourAccounts(self):
        with open_file('account_listing_aggregation.ofx') as f:
            ofx = OfxParser.parse(f)
        self.assertTrue(hasattr(ofx, 'accounts'))
        self.assertEqual(len(ofx.accounts), 4)

        # first account
        account = ofx.accounts[0]
        self.assertEqual(account.account_type, 'SAVINGS')
        self.assertEqual(account.desc, 'USAA SAVINGS')
        self.assertEqual(account.institution.organization, 'USAA')
        self.assertEqual(account.number, '0000000001')
        self.assertEqual(account.routing_number, '314074269')

        # second
        account = ofx.accounts[1]
        self.assertEqual(account.account_type, 'CHECKING')
        self.assertEqual(account.desc, 'FOUR STAR CHECKING')
        self.assertEqual(account.institution.organization, 'USAA')
        self.assertEqual(account.number, '0000000002')
        self.assertEqual(account.routing_number, '314074269')

        # third
        account = ofx.accounts[2]
        self.assertEqual(account.account_type, 'CREDITLINE')
        self.assertEqual(account.desc, 'LINE OF CREDIT')
        self.assertEqual(account.institution.organization, 'USAA')
        self.assertEqual(account.number, '00000000000003')
        self.assertEqual(account.routing_number, '314074269')

        # fourth
        account = ofx.accounts[3]
        self.assertEqual(account.account_type, '')
        self.assertEqual(account.desc, 'MY CREDIT CARD')
        self.assertEqual(account.institution.organization, 'USAA')
        self.assertEqual(account.number, '4111111111111111')


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
        with open_file('fail_nice/date_missing.ofx') as f:
            ofx = OfxParser.parse(f, False)
        self.assertEqual(len(ofx.account.statement.transactions), 0)
        self.assertEqual(len(ofx.account.statement.discarded_entries), 3)
        self.assertEqual(len(ofx.account.statement.warnings), 0)

        # Test that it raises an error otherwise.
        with open_file('fail_nice/date_missing.ofx') as f:
            self.assertRaises(OfxParserException, OfxParser.parse, f)

    def testDecimalConversionError(self):
        ''' The test file contains a transaction that has a poorly formatted
        decimal number ($20). Test that we catch this.
        '''
        with open_file('fail_nice/decimal_error.ofx') as f:
            ofx = OfxParser.parse(f, False)
        self.assertEqual(len(ofx.account.statement.transactions), 0)
        self.assertEqual(len(ofx.account.statement.discarded_entries), 1)

        # Test that it raises an error otherwise.
        with open_file('fail_nice/decimal_error.ofx') as f:
            self.assertRaises(OfxParserException, OfxParser.parse, f)

    def testEmptyBalance(self):
        ''' The test file contains empty or blank strings in the balance
        fields. Fail nicely on those.
        '''
        with open_file('fail_nice/empty_balance.ofx') as f:
            ofx = OfxParser.parse(f, False)
        self.assertEqual(len(ofx.account.statement.transactions), 1)
        self.assertEqual(len(ofx.account.statement.discarded_entries), 0)
        self.assertFalse(hasattr(ofx.account.statement, 'balance'))
        self.assertFalse(hasattr(ofx.account.statement, 'available_balance'))

        # Test that it raises an error otherwise.
        with open_file('fail_nice/empty_balance.ofx') as f:
            self.assertRaises(OfxParserException, OfxParser.parse, f)


class TestParseSonrs(TestCase):

    def testSuccess(self):
        with open_file('signon_success.ofx') as f:
            ofx = OfxParser.parse(f, True)
        self.assertTrue(ofx.signon.success)
        self.assertEqual(ofx.signon.code, 0)
        self.assertEqual(ofx.signon.severity, 'INFO')
        self.assertEqual(ofx.signon.message, 'Login successful')

        with open_file('signon_success_no_message.ofx') as f:
            ofx = OfxParser.parse(f, True)
        self.assertTrue(ofx.signon.success)
        self.assertEqual(ofx.signon.code, 0)
        self.assertEqual(ofx.signon.severity, 'INFO')
        self.assertEqual(ofx.signon.message, '')

    def testFailure(self):
        with open_file('signon_fail.ofx') as f:
            ofx = OfxParser.parse(f, True)
        self.assertFalse(ofx.signon.success)
        self.assertEqual(ofx.signon.code, 15500)
        self.assertEqual(ofx.signon.severity, 'ERROR')
        self.assertEqual(ofx.signon.message, 'Your request could not be processed because you supplied an invalid identification code or your password was incorrect')

if __name__ == "__main__":
    import unittest
    unittest.main()
