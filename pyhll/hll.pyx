from libc.stdlib cimport malloc, free


cdef extern from "stdint.h" nogil:

    ctypedef unsigned int uint32_t
    ctypedef unsigned int uint64_t


cdef extern from "hll_constants.h":
    pass


cdef extern from "hll.h":

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


cdef class Cardinality(object):
    cdef hll_t *_c_hll
    cdef int _initialized

    def __ciniit__(self):
        self._c_hll = <hll_t *>malloc(sizeof(hll_t))
        if self._c_hll is NULL:
            raise MemoryError("Can't create hll_t struct")
        self._initialized = hll_init(12, self._c_hll)
        assert self._initialized == 0

    def __dealloc__(self):
        if self._c_hll is not NULL:
            if self._initialized == 0:
                hll_destroy(self._c_hll)
            free(self._c_hll)
