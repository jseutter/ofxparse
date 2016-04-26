from __future__ import absolute_import

from ofxparse import OfxParser as op
from unittest import TestCase
import sys
sys.path.append('..')
from .support import open_file


class TestOfxWrite(TestCase):
    def test_write(self):
        test_file = open_file('fidelity.ofx')
        ofx_doc = op.parse(test_file)
        self.assertEqual(str(ofx_doc), "")

if __name__ == "__main__":
    import unittest
    unittest.main()
