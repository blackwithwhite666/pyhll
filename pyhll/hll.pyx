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
from libc.stdlib cimport malloc, free


cdef extern from "stdint.h" nogil:

    ctypedef unsigned int uint32_t
    ctypedef unsigned int uint64_t


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


MIN_PRECISION = HLL_MIN_PRECISION
MAX_PRECISION = HLL_MAX_PRECISION


cdef class Cardinality(object):
    """Compute cardinality of some set using HyperLogLog algorithm.

    :param prec: precision to use,
    :type prec: int
    """

    cdef hll_t *_c_hll
    cdef int _initialized
    cdef int _precision

    def __cinit__(self, int prec=12):
        self._initialized = -1
        if not (HLL_MIN_PRECISION <= prec <= HLL_MAX_PRECISION):
            raise ValueError('Wrong precision value "{0!r}" given'.format(prec))
        self._precision = prec
        self._c_hll = <hll_t *>malloc(sizeof(hll_t))
        if self._c_hll is NULL:
            raise MemoryError("Can't create hll_t struct")
        self._initialized = hll_init(self._precision, self._c_hll)
        assert self._initialized == 0, "initialization failed"

    def __dealloc__(self):
        if self._c_hll is not NULL:
            if self._initialized == 0:
                hll_destroy(self._c_hll)
            free(self._c_hll)

    property precision:

        def __get__(self):
            return self._precision

    property size:

        def __get__(self):
            return hll_size(self._c_hll)

    property count:

        def __get__(self):
            return int(self.size)

    def __len__(self):
        return self.count

    def add(self, bytes s):
        """Add one string."""
        cdef char* c_string = s
        hll_add(self._c_hll, c_string)

    def update(self, strings):
        """Add multiple strings at once."""
        for s in strings:
            self.add(s)

    def __repr__(self):
        return ('<{0}(size={2.size}) at {1}>'.
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
