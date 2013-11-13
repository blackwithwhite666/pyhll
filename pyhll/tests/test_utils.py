from __future__ import absolute_import

from pyhll.tests.base import TestCase
from pyhll import (
    bytes_for_precision,
    error_for_precision,
    precision_for_error,
    MIN_PRECISION,
    MAX_PRECISION,
)


class UtilsTest(TestCase):

    def test_bytes_for_precision(self):
        with self.assertRaises(ValueError):
            bytes_for_precision(MIN_PRECISION - 1)
        with self.assertRaises(ValueError):
            bytes_for_precision(MAX_PRECISION + 1)
        self.assertGreater(bytes_for_precision(MIN_PRECISION), 0)
        self.assertGreater(bytes_for_precision(MAX_PRECISION), 0)
        self.assertEqual(16, bytes_for_precision(4))
        self.assertEqual(3280, bytes_for_precision(12))
        self.assertEqual(52432, bytes_for_precision(16))

    def test_error_for_precision(self):
        with self.assertRaises(ValueError):
            error_for_precision(MIN_PRECISION - 1)
        with self.assertRaises(ValueError):
            error_for_precision(MAX_PRECISION + 1)
        self.assertGreater(error_for_precision(MIN_PRECISION), 0)
        self.assertGreater(error_for_precision(MAX_PRECISION), 0)
        self.assertAlmostEqual(0.26, error_for_precision(4))
        self.assertAlmostEqual(0.01625, error_for_precision(12))
        self.assertAlmostEqual(0.0040625, error_for_precision(16))

    def test_precision_for_error(self):
        with self.assertRaises(ValueError):
            precision_for_error(2.0)
        with self.assertRaises(ValueError):
            precision_for_error(-2.0)
        self.assertEqual(4, precision_for_error(0.26))
        self.assertEqual(12, precision_for_error(0.01625))
        self.assertEqual(16, precision_for_error(0.0040625))
