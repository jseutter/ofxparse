from __future__ import absolute_import

from ofxparse import OfxParser, OfxPrinter
from unittest import TestCase
from six import StringIO
from os import close, remove
from tempfile import mkstemp
import sys
sys.path.append('..')
from .support import open_file


class TestOfxWrite(TestCase):
    def test_write(self):
        with open_file('fidelity.ofx') as f:
            ofx = OfxParser.parse(f)
        self.assertEqual(str(ofx), "")

    def test_using_ofx_printer(self):
        with open_file('checking.ofx') as f:
            ofx = OfxParser.parse(f)
        fd, name = mkstemp()
        close(fd)
        printer = OfxPrinter(ofx=ofx, filename=name)
        printer.write(tabs=1)

    def test_using_ofx_printer_with_stringio(self):
        with open_file('checking.ofx') as f:
            ofx = OfxParser.parse(f)
        output_buffer = StringIO()
        printer = OfxPrinter(ofx=ofx, filename=None)
        printer.writeToFile(output_buffer, tabs=1)
        assert output_buffer.getvalue().startswith("OFXHEADER")

if __name__ == "__main__":
    import unittest
    unittest.main()
