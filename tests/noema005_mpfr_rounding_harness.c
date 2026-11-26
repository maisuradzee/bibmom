#define main noema_native_benchmark_main
#include "../scripts/noema005_native_accumulator_benchmark.c"
#undef main

#include <gmp.h>
#include <mpfr.h>

static int parse_units(const char *text, mpz_t units) {
    if (mpz_set_str(units, text, 10) != 0) return 0;

    mpz_t limit, minimum;
    mpz_inits(limit, minimum, NULL);
    mpz_ui_pow_ui(limit, 2, 2559);
    mpz_neg(minimum, limit);
    int in_range = mpz_cmp(units, minimum) >= 0 && mpz_cmp(units, limit) < 0;
    mpz_clears(limit, minimum, NULL);
    return in_range;
}

static int mpz_to_accumulator(const mpz_t units, exact_accum_t *value) {
    memset(value, 0, sizeof(*value));
    mpz_t magnitude;
    mpz_init(magnitude);
    mpz_abs(magnitude, units);
    size_t words = 0;
    mpz_export(value->limb, &words, -1, sizeof(value->limb[0]), 0, 0, magnitude);
    mpz_clear(magnitude);
    if (words > EXACT_LIMBS) return 0;

    if (mpz_sgn(units) < 0) {
        uint64_t carry = 1;
        for (int limb = 0; limb < EXACT_LIMBS; ++limb) {
            __uint128_t total = (__uint128_t)(~value->limb[limb]) + carry;
            value->limb[limb] = (uint64_t)total;
            carry = (uint64_t)(total >> 64);
        }
    }
    return 1;
}

int main(void) {
    char line[1024];
    mpz_t units;
    mpz_init(units);
    mpfr_t exact_reference;
    mpfr_init2(exact_reference, EXACT_LIMBS * 64 + 64);

    while (fgets(line, sizeof(line), stdin)) {
        line[strcspn(line, "\\r\\n")] = '\\0';
        if (!*line) continue;

        exact_accum_t accumulator;
        if (!parse_units(line, units) || !mpz_to_accumulator(units, &accumulator)) {
            fprintf(stderr, "invalid or out-of-range exact integer input\\n");
            mpfr_clear(exact_reference);
            mpz_clear(units);
            return 2;
        }

        mpfr_set_z(exact_reference, units, MPFR_RNDN);
        mpfr_div_2ui(exact_reference, exact_reference, 1074, MPFR_RNDN);
        double expected = mpfr_get_d(exact_reference, MPFR_RNDN);
        double actual = exact_to_binary64(&accumulator);

        uint64_t expected_bits = 0;
        uint64_t actual_bits = 0;
        memcpy(&expected_bits, &expected, sizeof(expected_bits));
        memcpy(&actual_bits, &actual, sizeof(actual_bits));
        if (expected_bits != actual_bits) {
            fprintf(
                stderr,
                "MPFR mismatch for input %s: expected %016" PRIx64 ", got %016" PRIx64 "\\n",
                line, expected_bits, actual_bits
            );
            mpfr_clear(exact_reference);
            mpz_clear(units);
            return 1;
        }
        printf("%016" PRIx64 "\\n", actual_bits);
    }

    int read_error = ferror(stdin);
    mpfr_clear(exact_reference);
    mpz_clear(units);
    return read_error ? 3 : 0;
}
