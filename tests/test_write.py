from __future__ import absolute_import

from ofxparse import OfxParser as op, OfxPrinter
from unittest import TestCase
from os import close, remove
from tempfile import mkstemp
import sys
sys.path.append('..')
from .support import open_file


class TestOfxWrite(TestCase):
    def test_write(self):
        test_file = open_file('fidelity.ofx')
        ofx_doc = op.parse(test_file)
        self.assertEqual(str(ofx_doc), "")

    def test_using_ofx_printer(self):
        test_file = open_file('checking.ofx')
        ofx_doc = op.parse(test_file)
        fd, name = mkstemp()
        close(fd)
        printer = OfxPrinter(ofx=ofx_doc, filename=name)
        printer.write(tabs=1)

if __name__ == "__main__":
    import unittest
    unittest.main()
