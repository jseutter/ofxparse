ofxparse
========

ofxparse is a parser for Open Financial Exchange (.ofx) format files.  OFX
files are available from almost any online banking site, so they work well
if you want to pull together your finances from multiple sources.  Online
trading accounts also provide account statements in OFX files.

There are three different types of OFX files, called BankAccount,
CreditAccount and InvestmentAccount files.  This library has been tested with
real-world samples of all three types.  If you find a file that does not work
with this library, please consider contributing the file so ofxparse can be
improved.  See the Help! section below for directions on how to do this.

Example Usage
=============

Here's a sample program

.. code:: python

  from ofxparse import OfxParser
  with codecs.open('file.ofx') as fileobj:
      ofx = OfxParser.parse(fileobj)
  ofx.accounts                        # An account with information
  ofx.account.number                  # The account number
  ofx.account.routing_number          # The transit id (sometimes called branch number)
  ofx.account.statement               # Account information for a period of time
  ofx.account.statement.start_date    # The start date of the transactions
  ofx.account.statement.end_date      # The end date of the transactions
  ofx.account.statement.transactions  # A list of account activities
  ofx.account.statement.balance       # The money in the account as of the statement date
  ofx.account.statement.available_balance # The money available from the account as of the statement date

Help!
=====

Sample ``.ofx`` and ``.qfx`` files are very useful.
If you want to help us out, please edit
all identifying information from the file and then email it to jseutter dot
ofxparse at gmail dot com.

Development
===========

Prerequisites::
  # Ubuntu
  sudo apt-get install python-beautifulsoup python-nose python-coverage-test-runner

  # pip for Python 3:
  pip install BeautifulSoup4 six lxml nose coverage

  # pip for Python 2:
  pip install BeautifulSoup six nose coverage

Tests:
Simply running the ``nosetests`` command should run the tests.

.. code:: bash

  nosetests

If you don't have nose installed, the following might also work:

.. code:: bash

  python -m unittest tests.test_parse

Test Coverage Report:

.. code:: bash

  coverage run -m unittest tests.test_parse
  
  # text report
  coverage report

  # html report
  coverage html
  firefox htmlcov/index.html


Homepage
========
| Homepage: https://sites.google.com/site/ofxparse
| Source: https://github.com/jseutter/ofxparse

License
=======

ofxparse is released under an MIT license.  See the LICENSE file for the actual
license text.  The basic idea is that if you can use Python to do what you are
doing, you can also use this library.


