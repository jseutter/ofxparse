python-ofx: ofx utilities for python

Example usage:

from ofx_parse import OfxParser

ofx = OfxParser.parse(file('file.ofx'))
ofx.account                         # An account with information
ofx.account.number                  # The account number
ofx.account.routing_number          # The transit id (sometimes called branch number)
ofx.account.statement               # Account information for a period of time
ofx.account.statement.start_date    # The start date of the transactions
ofx.account.statement.end_date      # The end date of the transactions
ofx.account.statement.transactions  # A list of account activities
ofx.account.statement.balance       # The money in the account as of the statement date
ofx.account.statement.available_balance # The money available from the account as of the statement date


Requirements:
- The library will parse all elements of my PCF bank account statement.
- The library will pass all unit tests.
- The library will be packaged as a distutils package
- The library will run on Python 2.5.1 on os x.
- The library will have a well-defined API.
- The library will be released under the same license as Python.
- The library will be hosted on a popular hosting service using git.
- The library will be supported with a mailing list.
- The library will be available on the Python Package Index.

Design:
- The library will use BeautifulSoup for parsing the ofx file format.
- The library will parse and make available the following data items:
 - OFXHEADER:100
 - DATA:OFXSGML
 - VERSION:102
 - SECURITY:NONE
 - ENCODING:USASCII
 - CHARSET:1252
 - COMPRESSION:NONE
 - OLDFILEUID:NONE
 - NEWFILEUID:NONE
 - <OFX>
 - <OFX><SIGNONMSGSRSV1>
 - <OFX><SIGNONMSGSRSV1><SONRS>
 - <OFX><SIGNONMSGSRSV1><SONRS><STATUS>
 - <OFX><SIGNONMSGSRSV1><SONRS><STATUS><CODE>0
 - <OFX><SIGNONMSGSRSV1><SONRS><STATUS><SEVERITY>INFO
 - <OFX><SIGNONMSGSRSV1><SONRS><STATUS><MESSAGE>OK
 - <OFX><SIGNONMSGSRSV1><SONRS><STATUS></STATUS>
 - <OFX><SIGNONMSGSRSV1><SONRS><DTSERVER>20090523122017
 - <OFX><SIGNONMSGSRSV1><SONRS><LANGUAGE>ENG
 - <OFX><SIGNONMSGSRSV1><SONRS><DTPROFUP>20090523122017
 - <OFX><SIGNONMSGSRSV1><SONRS><DTACCTUP>20090523122017
 - <OFX><SIGNONMSGSRSV1><SONRS><INTU.BID>00024
 - <OFX><SIGNONMSGSRSV1><SONRS></SONRS>
 - <OFX><SIGNONMSGSRSV1></SIGNONMSGSRSV1>
 - <OFX><BANKMSGSRSV1>
 - <OFX><BANKMSGSRSV1><STMTTRNRS>
 - <OFX><BANKMSGSRSV1><STMTTRNRS><TRNUID>20090523122017
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STATUS>
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STATUS><CODE>0
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STATUS><CODE>0<SEVERITY>INFO
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STATUS><CODE>0<SEVERITY>INFO<MESSAGE>OK
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STATUS></STATUS>
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><CURDEF>CAD
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><BANKACCTFROM>
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><BANKACCTFROM><BANKID>160000100
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><BANKACCTFROM><ACCTID>30800 000016818411
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><BANKACCTFROM><ACCTTYPE>CHECKING
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><BANKACCTFROM></BANKACCTFROM>
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><BANKTRANLIST>
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><BANKTRANLIST><DTSTART>20090401
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><BANKTRANLIST><DTEND>20090523122017
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><BANKTRANLIST><STMTTRN>
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><BANKTRANLIST><STMTTRN><TRNTYPE>POS
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><BANKTRANLIST><STMTTRN><DTPOSTED>20090401122017.000[-5:EST]
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><BANKTRANLIST><STMTTRN><TRNAMT>-6.60
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><BANKTRANLIST><STMTTRN><FITID>0000168184112009040100001
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><BANKTRANLIST><STMTTRN><NAME>MCDONALD'S #112
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><BANKTRANLIST><STMTTRN><MEMO>POS MERCHANDISE;MCDONALD'S #112
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><BANKTRANLIST><STMTTRN></STMTTRN>
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><BANKTRANLIST></BANKTRANLIST>
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><LEDGERBAL>
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><LEDGERBAL><BALAMT>382.34
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><LEDGERBAL><DTASOF>20090523122017
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><LEDGERBAL></LEDGERBAL>
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><AVAILBAL>
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><AVAILBAL><BALAMT>682.34
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS><AVAILBAL></AVAILBAL>
 - <OFX><BANKMSGSRSV1><STMTTRNRS><STMTRS></STMTRS>
 - <OFX><BANKMSGSRSV1><STMTTRNRS></STMTTRNRS>
 - <OFX><BANKMSGSRSV1></BANKMSGSRSV1>
 - <OFX></OFX>


 ========================
 
 Account - BankAccount, CreditAccount, InvestmentAccount
 Statement
 Transaction
 Institute

 
 License:
 Todo: Figure out what license to release this software with
 I have been recommended the MIT or LGPL licenses
 
 Homepage:
 Todo: Figure out where to host this software
 I have been recommended GitHub over Google Code
 Also look at using google code with google sites for the web stuff - note, no git on Google.
 
 