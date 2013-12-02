"""This is a wrapper to HyperLogLog implementation on C.

HyperLogLog's are a relatively new sketching data structure.
They are used to estimate cardinality, i.e. the unique number
of items in a set. They are based on the observation that any bit
in a "good" hash function is indepedenent of any other bit
and that the probability of getting a string of N bits all set
to the same value is 1/(2^N). There is a lot more in the math,
but that is the basic intuition. What is even more incredible
is that the storage required to do the counting is log(log(N)).
So with a 6 bit register, we can count well into the trillions.
"""
from cpython cimport array
from libc.stdlib cimport malloc, free


cdef extern from "stdint.h" nogil:

    ctypedef unsigned int uint32_t
    ctypedef unsigned long uint64_t


cdef extern from "hll_constants.h":
    pass


cdef extern from "hll.h":

    int HLL_MIN_PRECISION
    int HLL_MAX_PRECISION

    ctypedef struct hll_t:
        unsigned char precision
        uint32_t *registers

    int hll_init(unsigned char precision, hll_t *h)
    int hll_destroy(hll_t *h)

    void hll_add(hll_t *h, char *key)
    void hll_add_hash(hll_t *h, uint64_t hash)
    double hll_size(hll_t *h)
    int hll_precision_for_error(double err)
    double hll_error_for_precision(int prec)
    uint64_t hll_bytes_for_precision(int prec)
    int hll_merge(hll_t *h, hll_t *first, hll_t *second)
    int hll_words(hll_t *h)


MIN_PRECISION = HLL_MIN_PRECISION
MAX_PRECISION = HLL_MAX_PRECISION


def recreate_cardinality(int prec, array.array a):
    """Restore pickled set."""
    cdef Cardinality c = Cardinality(prec)
    c.load_registers(a)
    return c


cdef class Cardinality(object):
    """Compute cardinality of some set using HyperLogLog algorithm.

    :param prec: precision to use,
    :type prec: int
    """

    cdef hll_t *_c_hll
    cdef int _initialized

    def __cinit__(self, int prec=12):
        self._initialized = -1
        if not (HLL_MIN_PRECISION <= prec <= HLL_MAX_PRECISION):
            raise ValueError('Wrong precision value "{0!r}" given'.format(prec))
        self._c_hll = <hll_t *>malloc(sizeof(hll_t))
        if self._c_hll is NULL:
            raise MemoryError("Can't create hll_t struct")
        self._initialized = hll_init(prec, self._c_hll)
        assert self._initialized == 0, "initialization failed"

    def __dealloc__(self):
        if self._c_hll is not NULL:
            if self._initialized == 0:
                hll_destroy(self._c_hll)
            free(self._c_hll)

    cdef array.array dump_registers(self):
        cdef int words = hll_words(self._c_hll)
        cdef array.array a = array.array('I')
        array.resize(a, words)
        cdef unsigned int* u = a.data.as_uints
        cdef unsigned int i
        for i in range(words):
            u[i] = self._c_hll.registers[i]
        return a

    cdef load_registers(self, array.array a):
        cdef int words = hll_words(self._c_hll)
        if len(a) != words:
            raise ValueError("Given array has wrong length.")
        cdef unsigned int* u = a.data.as_uints
        cdef unsigned int i
        for i in range(words):
            self._c_hll.registers[i] = u[i]

    property precision:

        def __get__(self):
            return self._c_hll.precision

    property cardinality:

        def __get__(self):
            return hll_size(self._c_hll)

    property count:

        def __get__(self):
            return int(self.cardinality)

    def __len__(self):
        return self.count

    def error(self):
        """Return error value."""
        return error_for_precision(self._c_hll.precision)

    def sizeof(self):
        """Return size of object."""
        return bytes_for_precision(self._c_hll.precision)

    def add(self, bytes s):
        """Add one string."""
        cdef char* c_string = s
        hll_add(self._c_hll, c_string)
        return self

    def update(self, strings):
        """Add multiple strings at once."""
        for s in strings:
            self.add(s)
        return self

    def union(self, Cardinality other):
        """Return union of two set."""
        cdef Cardinality c = Cardinality(self.precision)
        cdef int result = hll_merge(c._c_hll, self._c_hll, other._c_hll)
        if result == -1:
            raise ValueError("Can't merge sets!")
        return c

    def __or__(self, Cardinality other):
        return self.union(other)

    def __reduce__(self):
        return (recreate_cardinality, (self.precision, self.dump_registers()))

    def __repr__(self):
        return ('<{0}(cardinality={2.cardinality}) at {1}>'.
                format(self.__class__.__name__, hex(id(self)), self))


def precision_for_error(double err):
    """Get precision for given error value."""
    cdef int result = hll_precision_for_error(err)
    if result == -1:
        raise ValueError('Wrong error value "{0!r}" given'.format(err))
    return result


def error_for_precision(int prec):
    """Return error for given precision."""
    cdef double result = hll_error_for_precision(prec)
    if result == 0:
        raise ValueError('Wrong precision value "{0!r}" given'.format(prec))
    return result


def bytes_for_precision(int prec):
    """Get needed memory in bytes for given precision."""
    cdef uint64_t result = hll_bytes_for_precision(prec)
    if result == 0:
        raise ValueError('Wrong precision value "{0!r}" given'.format(prec))
    return result
