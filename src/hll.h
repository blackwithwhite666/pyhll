#include <stdint.h>

#ifndef HLL_H
#define HLL_H

// Ensure precision in a sane bound
#define HLL_MIN_PRECISION 4      // 16 registers
#define HLL_MAX_PRECISION 18     // 262,144 registers

typedef struct {
    unsigned char precision;
    uint32_t *registers;
} hll_t;

/**
 * Initializes a new HLL
 * @arg precision The digits of precision to use
 * @arg h The HLL to initialize
 * @return 0 on success
 */
int hll_init(unsigned char precision, hll_t *h);

/**
 * Destroys an hll.
 * @return 0 on success
 */
int hll_destroy(hll_t *h);

/**
 * Adds a new key to the HLL
 * @arg h The hll to add to
 * @arg key The key to add
 */
void hll_add(hll_t *h, char *key);

/**
 * Adds a new hash to the HLL
 * @arg h The hll to add to
 * @arg hash The hash to add
 */
void hll_add_hash(hll_t *h, uint64_t hash);

/**
 * Estimates the cardinality of the HLL
 * @arg h The hll to query
 * @return An estimate of the cardinality
 */
double hll_size(hll_t *h);

/**
 * Computes the minimum digits of precision
 * needed to hit a target error.
 * @arg error The target error rate
 * @return The number of digits needed, or
 * negative on error.
 */
int hll_precision_for_error(double err);

/**
 * Computes the upper bound on variance given
 * a precision
 * @arg prec The precision to use
 * @return The expected variance in the count,
 * or zero on error.
 */
double hll_error_for_precision(int prec);

/**
 * Computes the bytes required for a HLL of the
 * given precision.
 * @arg prec The precision to use
 * @return The bytes required or 0 on error.
 */
uint64_t hll_bytes_for_precision(int prec);

/**
 * Return union of two sets.
 * @arg h The merged HLL
 * @arg first The first HLL to merge
 * @arg second The second HLL to merge
 * @return 0 on success
 */
int hll_merge(hll_t *h, hll_t *first, hll_t *second);

/**
 * Estimates words count of the HLL
 * @arg h The hll to query
 * @return An words count
 */
int hll_words(hll_t *h);

#endif
