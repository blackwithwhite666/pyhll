from __future__ import absolute_import

try:
    from cPickle import dumps, loads
except ImportError:
    from pickle import dumps, loads

from pyhll.tests.base import TestCase
from pyhll import Cardinality, MIN_PRECISION, MAX_PRECISION


class CardinalityTest(TestCase):

    def test_construct(self):
        with self.assertRaises(ValueError):
            Cardinality(MIN_PRECISION - 1)
        with self.assertRaises(ValueError):
            Cardinality(MAX_PRECISION + 1)
        self.assertEqual(MIN_PRECISION, Cardinality(MIN_PRECISION).precision)
        self.assertEqual(MAX_PRECISION, Cardinality(MAX_PRECISION).precision)

    def test_cardinality(self):
        t = (b'foo', b'bar')
        c = Cardinality()
        c.update(t)
        self.assertAlmostEqual(len(t), c.cardinality, places=1)

    def test_count(self):
        t = (b'foo', b'bar')
        c = Cardinality()
        c.update((b'foo', b'bar'))
        self.assertEqual(len(t), c.count)
        self.assertEqual(len(t), len(c))

    def test_add(self):
        c = Cardinality()
        c.add(b'foo')
        self.assertEqual(1, len(c))
        c.add(b'bar')
        self.assertEqual(2, len(c))
        with self.assertRaises(TypeError):
            c.add(u'foo')
        with self.assertRaises(TypeError):
            c.add(1)

    def test_update(self):
        c = Cardinality()
        c.update([b'foo', b'baz'])
        self.assertEqual(2, len(c))
        c.update([b'bar', b'boz'])
        self.assertEqual(4, len(c))

    def test_union(self):
        c1 = Cardinality()
        c2 = Cardinality()
        c1.add('foo')
        c2.add('bar')
        self.assertEqual(2, len(c1.union(c2)))
        c1.add('bar')
        self.assertEqual(2, len(c1 | c2))

    def test_pickle(self):
        c = Cardinality()
        c.add('foo')
        c.add('bar')
        self.assertEqual(2, len(c))
        dump = dumps(c)
        restored_c = loads(dump)
        self.assertEqual(2, len(restored_c))
