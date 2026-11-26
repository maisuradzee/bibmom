#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <float.h>
#include <inttypes.h>
#include <math.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <time.h>

#define MAX_WORKERS 256
#define MAX_REPETITIONS 1000
#define EXACT_LIMBS 40
#define LARGE_VALUE 9007199254740992.0 /* 2^53 */

typedef enum { LAYOUT_TRIPLET, LAYOUT_GROUPED } layout_t;
typedef enum {
    SERIAL_NAIVE, SERIAL_LONG_DOUBLE, SERIAL_PAIRWISE, SERIAL_NEUMAIER,
    SERIAL_EXACT, OMP_NAIVE, OMP_LONG_DOUBLE, OMP_PAIRWISE,
    OMP_NEUMAIER, OMP_EXACT
} method_t;

typedef struct { uint64_t limb[EXACT_LIMBS]; } exact_accum_t;

_Static_assert(sizeof(double) == sizeof(uint64_t), "NOEMA exact conversion requires 64-bit double storage");
_Static_assert(DBL_MANT_DIG == 53 && DBL_MAX_EXP == 1024 && DBL_MIN_EXP == -1021,
               "NOEMA exact conversion requires IEEE-754 binary64 double");
typedef struct {
    const char *name;
    double *wall_samples;
    double *cpu_samples;
    double median_wall_ns;
    double median_cpu_ns;
    double speedup;
    int correct_runs;
    int actual_min;
    int actual_max;
} result_t;

static int parse_positive(const char *s, long long *out) {
    char *end = NULL; errno = 0;
    long long value = strtoll(s, &end, 10);
    if (errno || !end || *end || value < 1) return 0;
    *out = value; return 1;
}
static int parse_nonnegative(const char *s, int *out) {
    char *end = NULL; errno = 0;
    long value = strtol(s, &end, 10);
    if (errno || !end || *end || value < 0 || value > MAX_REPETITIONS) return 0;
    *out = (int)value; return 1;
}
static int parse_workers(const char *s, int out[MAX_WORKERS], int *count) {
    char *copy = strdup(s); if (!copy) return 0;
    int n = 0; char *save = NULL;
    for (char *token = strtok_r(copy, ",", &save); token; token = strtok_r(NULL, ",", &save)) {
        long long value = 0;
        if (!parse_positive(token, &value) || value > MAX_WORKERS || n >= MAX_WORKERS) { free(copy); return 0; }
        for (int i = 0; i < n; ++i) if (out[i] == (int)value) { free(copy); return 0; }
        out[n++] = (int)value;
    }
    free(copy); *count = n; return n > 0;
}
static double value_at(long long i, long long repeats, layout_t layout) {
    if (layout == LAYOUT_TRIPLET) {
        switch (i % 3) { case 0: return LARGE_VALUE; case 1: return 1.0; default: return -LARGE_VALUE; }
    }
    if (i < repeats) return LARGE_VALUE;
    if (i < 2 * repeats) return 1.0;
    return -LARGE_VALUE;
}
static void neumaier_add(double x, double *sum, double *correction) {
    double t = *sum + x;
    if (fabs(*sum) >= fabs(x)) *correction += (*sum - t) + x;
    else *correction += (x - t) + *sum;
    *sum = t;
}
static void add_word(exact_accum_t *a, int index, uint64_t value) {
    if (!value) return;
    __uint128_t total = (__uint128_t)a->limb[index] + value;
    a->limb[index] = (uint64_t)total;
    uint64_t carry = (uint64_t)(total >> 64);
    for (int i = index + 1; carry && i < EXACT_LIMBS; ++i) {
        uint64_t old = a->limb[i]; a->limb[i] = old + 1;
        carry = (a->limb[i] == 0);
    }
    /* Fixed-width two's-complement wrap is intentional for negative values. */
}
static void subtract_word(exact_accum_t *a, int index, uint64_t value) {
    if (!value) return;
    uint64_t old = a->limb[index]; a->limb[index] = old - value;
    uint64_t borrow = old < value;
    for (int i = index + 1; borrow && i < EXACT_LIMBS; ++i) {
        old = a->limb[i]; a->limb[i] = old - 1;
        borrow = (old == 0);
    }
    /* Borrow through the top limb forms the two's-complement negative value. */
}
static void exact_add_significand(exact_accum_t *a, uint64_t significand, int shift, int negative) {
    if (!significand) return;
    int index = shift / 64; int offset = shift % 64;
    uint64_t low = significand << offset;
    uint64_t high = offset ? significand >> (64 - offset) : 0;
    if (negative) { subtract_word(a, index, low); if (high) subtract_word(a, index + 1, high); }
    else { add_word(a, index, low); if (high) add_word(a, index + 1, high); }
}
static void exact_add_double(exact_accum_t *a, double value) {
    uint64_t bits = 0; memcpy(&bits, &value, sizeof(bits));
    uint64_t exponent = (bits >> 52) & 0x7ffu;
    uint64_t fraction = bits & UINT64_C(0x000fffffffffffff);
    if (exponent == 0x7ffu) { fprintf(stderr, "non-finite input to exact accumulator\n"); exit(3); }
    uint64_t significand = exponent ? (UINT64_C(1) << 52) | fraction : fraction;
    int shift = exponent ? (int)exponent - 1 : 0;
    exact_add_significand(a, significand, shift, (int)(bits >> 63));
}
static void exact_merge(exact_accum_t *target, const exact_accum_t *source) {
    uint64_t carry = 0;
    for (int i = 0; i < EXACT_LIMBS; ++i) {
        __uint128_t total = (__uint128_t)target->limb[i] + source->limb[i] + carry;
        target->limb[i] = (uint64_t)total;
        carry = (uint64_t)(total >> 64);
    }
    /* The 2560-bit accumulator is modular; experiment bounds keep magnitude below its range. */
}
static int exact_equals_integer(const exact_accum_t *value, uint64_t expected) {
    exact_accum_t reference = {{0}};
    exact_add_significand(&reference, expected, 1074, 0);
    return memcmp(value, &reference, sizeof(reference)) == 0;
}
static int exact_equals_double(const exact_accum_t *value, double expected) {
    exact_accum_t reference = {{0}};
    exact_add_double(&reference, expected);
    return memcmp(value, &reference, sizeof(reference)) == 0;
}

static int exact_get_bit(const exact_accum_t *value, int bit) {
    if (bit < 0 || bit >= EXACT_LIMBS * 64) return 0;
    return (int)((value->limb[bit / 64] >> (bit % 64)) & UINT64_C(1));
}

static int exact_any_bits_below(const exact_accum_t *value, int exclusive) {
    if (exclusive <= 0) return 0;
    int full_words = exclusive / 64;
    if (full_words > EXACT_LIMBS) full_words = EXACT_LIMBS;
    for (int i = 0; i < full_words; ++i) {
        if (value->limb[i]) return 1;
    }
    int remainder = exclusive % 64;
    if (remainder && full_words < EXACT_LIMBS) {
        uint64_t mask = (UINT64_C(1) << remainder) - UINT64_C(1);
        if (value->limb[full_words] & mask) return 1;
    }
    return 0;
}

static uint64_t exact_shifted_low_u64(const exact_accum_t *value, int shift) {
    int word = shift / 64;
    int offset = shift % 64;
    if (word >= EXACT_LIMBS) return 0;
    uint64_t result = value->limb[word] >> offset;
    if (offset && word + 1 < EXACT_LIMBS) {
        result |= value->limb[word + 1] << (64 - offset);
    }
    return result;
}

static int exact_highest_bit(const exact_accum_t *value) {
    for (int word = EXACT_LIMBS - 1; word >= 0; --word) {
        uint64_t current = value->limb[word];
        if (!current) continue;
        for (int bit = 63; bit >= 0; --bit) {
            if ((current >> bit) & UINT64_C(1)) return word * 64 + bit;
        }
    }
    return -1;
}

/* Convert the exact signed integer in units of 2^-1074 to binary64.
   The caller must keep the exact sum inside the 2560-bit accumulator range. */
static double exact_to_binary64(const exact_accum_t *value) {
    exact_accum_t magnitude = *value;
    int negative = (int)(magnitude.limb[EXACT_LIMBS - 1] >> 63);
    if (negative) {
        uint64_t carry = 1;
        for (int i = 0; i < EXACT_LIMBS; ++i) {
            __uint128_t total = (__uint128_t)(~magnitude.limb[i]) + carry;
            magnitude.limb[i] = (uint64_t)total;
            carry = (uint64_t)(total >> 64);
        }
    }

    int highest = exact_highest_bit(&magnitude);
    uint64_t bits = negative ? (UINT64_C(1) << 63) : 0;
    if (highest < 0) return 0.0;

    if (highest <= 51) {
        /* Every integer multiple of the minimum subnormal is representable. */
        bits |= magnitude.limb[0];
    } else {
        int discarded = highest - 52;
        uint64_t significand = exact_shifted_low_u64(&magnitude, discarded)
            & ((UINT64_C(1) << 53) - UINT64_C(1));
        if (discarded > 0) {
            int guard = exact_get_bit(&magnitude, discarded - 1);
            int sticky = exact_any_bits_below(&magnitude, discarded - 1);
            if (guard && (sticky || (significand & UINT64_C(1)))) {
                ++significand;
                if (significand == (UINT64_C(1) << 53)) {
                    significand >>= 1;
                    ++highest;
                }
            }
        }

        int exponent_field = highest - 51;
        if (exponent_field >= 0x7ff) {
            /* Round-to-nearest overflow is represented by signed infinity. */
            bits |= UINT64_C(0x7ff) << 52;
        } else {
            bits |= (uint64_t)exponent_field << 52;
            bits |= significand & ((UINT64_C(1) << 52) - UINT64_C(1));
        }
    }

    double result;
    memcpy(&result, &bits, sizeof(result));
    return result;
}

static int exact_rounds_to_double(const exact_accum_t *value, double expected) {
    double actual = exact_to_binary64(value);
    uint64_t actual_bits = 0, expected_bits = 0;
    memcpy(&actual_bits, &actual, sizeof(actual_bits));
    memcpy(&expected_bits, &expected, sizeof(expected_bits));
    return actual_bits == expected_bits;
}

static int exact_accumulator_rounding_self_test(void) {
    exact_accum_t value = {{0}};
    exact_add_double(&value, 1.0);
    exact_add_double(&value, ldexp(1.0, -53));
    if (!exact_rounds_to_double(&value, 1.0)) return 0; /* halfway, even lower */

    value = (exact_accum_t){{0}};
    double odd_lower = nextafter(1.0, 2.0);
    exact_add_double(&value, odd_lower);
    exact_add_double(&value, ldexp(1.0, -53));
    if (!exact_rounds_to_double(&value, nextafter(odd_lower, 2.0))) return 0; /* halfway, even upper */

    value = (exact_accum_t){{0}};
    exact_add_double(&value, -1.0);
    exact_add_double(&value, -ldexp(1.0, -53));
    if (!exact_rounds_to_double(&value, -1.0)) return 0;

    value = (exact_accum_t){{0}};
    exact_add_double(&value, DBL_TRUE_MIN);
    exact_add_double(&value, DBL_TRUE_MIN);
    if (!exact_rounds_to_double(&value, 2.0 * DBL_TRUE_MIN)) return 0;

    value = (exact_accum_t){{0}};
    exact_add_double(&value, DBL_MIN);
    exact_add_double(&value, -DBL_TRUE_MIN);
    if (!exact_rounds_to_double(&value, nextafter(DBL_MIN, 0.0))) return 0;

    value = (exact_accum_t){{0}};
    exact_add_double(&value, DBL_MAX);
    exact_add_double(&value, nextafter(ldexp(1.0, 970), 0.0));
    if (!exact_rounds_to_double(&value, DBL_MAX)) return 0;

    value = (exact_accum_t){{0}};
    exact_add_double(&value, DBL_MAX);
    exact_add_double(&value, ldexp(1.0, 970));
    if (!exact_rounds_to_double(&value, INFINITY)) return 0;

    value = (exact_accum_t){{0}};
    exact_add_double(&value, -DBL_MAX);
    exact_add_double(&value, -ldexp(1.0, 970));
    if (!exact_rounds_to_double(&value, -INFINITY)) return 0;

    value = (exact_accum_t){{0}};
    exact_add_double(&value, LARGE_VALUE);
    exact_add_double(&value, 1.0);
    exact_add_double(&value, -LARGE_VALUE);
    return exact_rounds_to_double(&value, 1.0);
}

static int exact_accumulator_self_test(void) {
    exact_accum_t value = {{0}};
    exact_add_double(&value, LARGE_VALUE);
    exact_add_double(&value, 1.0);
    exact_add_double(&value, -LARGE_VALUE);
    exact_add_double(&value, 0.5);
    exact_add_double(&value, -0.25);
    exact_add_double(&value, DBL_TRUE_MIN);
    exact_add_double(&value, -DBL_TRUE_MIN);
    if (!exact_equals_double(&value, 1.25)) return 0;
    exact_add_double(&value, -2.5);
    if (!exact_equals_double(&value, -1.25)) return 0;
    return exact_accumulator_rounding_self_test();
}
static double pairwise_range(long long begin, long long end, long long repeats, layout_t layout) {
    long long n = end - begin;
    if (n <= 0) return 0.0;
    if (n == 1) return value_at(begin, repeats, layout);
    long long middle = begin + n / 2;
    return pairwise_range(begin, middle, repeats, layout) + pairwise_range(middle, end, repeats, layout);
}
static double pairwise_array(const double *values, int n) {
    if (n <= 0) return 0.0;
    if (n == 1) return values[0];
    int middle = n / 2;
    return pairwise_array(values, middle) + pairwise_array(values + middle, n - middle);
}
static const char *method_name(method_t m) {
    switch (m) {
        case SERIAL_NAIVE: return "serial_naive";
        case SERIAL_LONG_DOUBLE: return "serial_long_double";
        case SERIAL_PAIRWISE: return "serial_pairwise";
        case SERIAL_NEUMAIER: return "serial_neumaier";
        case SERIAL_EXACT: return "serial_exact_superaccumulator";
        case OMP_NAIVE: return "openmp_naive_partials";
        case OMP_LONG_DOUBLE: return "openmp_long_double";
        case OMP_PAIRWISE: return "openmp_pairwise_tree";
        case OMP_NEUMAIER: return "openmp_neumaier_state";
        default: return "openmp_exact_superaccumulator";
    }
}
static int is_openmp(method_t m) { return m >= OMP_NAIVE; }
static method_t serial_baseline(method_t m) {
    switch (m) {
        case OMP_NAIVE: return SERIAL_NAIVE;
        case OMP_LONG_DOUBLE: return SERIAL_LONG_DOUBLE;
        case OMP_PAIRWISE: return SERIAL_PAIRWISE;
        case OMP_NEUMAIER: return SERIAL_NEUMAIER;
        case OMP_EXACT: return SERIAL_EXACT;
        default: return m;
    }
}
static int run_once(long long repeats, layout_t layout, method_t method, int requested, int *actual_threads) {
    long long count = 3 * repeats;
    *actual_threads = 1;
    if (!is_openmp(method)) {
        if (method == SERIAL_NAIVE) {
            double sum = 0.0; for (long long i = 0; i < count; ++i) sum += value_at(i, repeats, layout);
            return sum == (double)repeats;
        }
        if (method == SERIAL_LONG_DOUBLE) {
            long double sum = 0.0L; for (long long i = 0; i < count; ++i) sum += (long double)value_at(i, repeats, layout);
            return sum == (long double)repeats;
        }
        if (method == SERIAL_PAIRWISE) return pairwise_range(0, count, repeats, layout) == (double)repeats;
        if (method == SERIAL_NEUMAIER) {
            double sum = 0.0, correction = 0.0;
            for (long long i = 0; i < count; ++i) neumaier_add(value_at(i, repeats, layout), &sum, &correction);
            return sum + correction == (double)repeats;
        }
        exact_accum_t exact = {{0}};
        for (long long i = 0; i < count; ++i) exact_add_double(&exact, value_at(i, repeats, layout));
        return exact_equals_integer(&exact, (uint64_t)repeats);
    }

    double *double_sums = calloc((size_t)requested, sizeof(double));
    double *corrections = calloc((size_t)requested, sizeof(double));
    long double *long_sums = calloc((size_t)requested, sizeof(long double));
    exact_accum_t *exact_states = calloc((size_t)requested, sizeof(exact_accum_t));
    if (!double_sums || !corrections || !long_sums || !exact_states) { fprintf(stderr, "worker-state allocation failed\n"); exit(2); }
    int actual = 0;
#pragma omp parallel num_threads(requested) shared(actual, double_sums, corrections, long_sums, exact_states)
    {
        int tid = omp_get_thread_num();
#pragma omp single
        actual = omp_get_num_threads();
        long long begin = count * tid / actual;
        long long end = count * (tid + 1) / actual;
        if (method == OMP_PAIRWISE) {
            double_sums[tid] = pairwise_range(begin, end, repeats, layout);
        } else {
            for (long long i = begin; i < end; ++i) {
                double value = value_at(i, repeats, layout);
                if (method == OMP_NAIVE) double_sums[tid] += value;
                else if (method == OMP_LONG_DOUBLE) long_sums[tid] += (long double)value;
                else if (method == OMP_NEUMAIER) neumaier_add(value, &double_sums[tid], &corrections[tid]);
                else exact_add_double(&exact_states[tid], value);
            }
        }
    }
    *actual_threads = actual;
    int correct = 0;
    if (method == OMP_NAIVE) {
        double sum = 0.0; for (int i = 0; i < actual; ++i) sum += double_sums[i];
        correct = sum == (double)repeats;
    } else if (method == OMP_LONG_DOUBLE) {
        long double sum = 0.0L; for (int i = 0; i < actual; ++i) sum += long_sums[i];
        correct = sum == (long double)repeats;
    } else if (method == OMP_PAIRWISE) {
        correct = pairwise_array(double_sums, actual) == (double)repeats;
    } else if (method == OMP_NEUMAIER) {
        double sum = 0.0, correction = 0.0;
        for (int i = 0; i < actual; ++i) { neumaier_add(double_sums[i], &sum, &correction); neumaier_add(corrections[i], &sum, &correction); }
        correct = sum + correction == (double)repeats;
    } else {
        exact_accum_t merged = {{0}};
        for (int i = 0; i < actual; ++i) exact_merge(&merged, &exact_states[i]);
        correct = exact_equals_integer(&merged, (uint64_t)repeats);
    }
    free(double_sums); free(corrections); free(long_sums); free(exact_states);
    return correct;
}
static double clock_ns(clockid_t id) {
    struct timespec ts; if (clock_gettime(id, &ts) != 0) { perror("clock_gettime"); exit(2); }
    return (double)ts.tv_sec * 1e9 + (double)ts.tv_nsec;
}
static int compare_double(const void *a, const void *b) {
    double x = *(const double *)a, y = *(const double *)b; return (x > y) - (x < y);
}
static double median_copy(const double *values, int n) {
    double *copy = malloc((size_t)n * sizeof(double)); if (!copy) exit(2);
    memcpy(copy, values, (size_t)n * sizeof(double)); qsort(copy, (size_t)n, sizeof(double), compare_double);
    double result = n % 2 ? copy[n / 2] : (copy[n / 2 - 1] + copy[n / 2]) / 2.0; free(copy); return result;
}
static result_t measure(long long repeats, layout_t layout, method_t method, int workers,
                        int warmups, int repetitions, double baseline) {
    result_t r = {0}; r.name = method_name(method); r.actual_min = MAX_WORKERS; r.actual_max = 0;
    r.wall_samples = calloc((size_t)repetitions, sizeof(double)); r.cpu_samples = calloc((size_t)repetitions, sizeof(double));
    if (!r.wall_samples || !r.cpu_samples) { fprintf(stderr, "sample allocation failed\n"); exit(2); }
    for (int i = 0; i < warmups + repetitions; ++i) {
        int actual = 1; double cpu_start = clock_ns(CLOCK_PROCESS_CPUTIME_ID); double wall_start = clock_ns(CLOCK_MONOTONIC);
        int correct = run_once(repeats, layout, method, workers, &actual);
        double wall = clock_ns(CLOCK_MONOTONIC) - wall_start; double cpu = clock_ns(CLOCK_PROCESS_CPUTIME_ID) - cpu_start;
        if (i >= warmups) {
            int slot = i - warmups; r.wall_samples[slot] = wall; r.cpu_samples[slot] = cpu;
            r.correct_runs += correct; if (actual < r.actual_min) r.actual_min = actual; if (actual > r.actual_max) r.actual_max = actual;
        }
    }
    r.median_wall_ns = median_copy(r.wall_samples, repetitions); r.median_cpu_ns = median_copy(r.cpu_samples, repetitions);
    r.speedup = is_openmp(method) && baseline > 0.0 ? baseline / r.median_wall_ns : 1.0;
    return r;
}
static void print_case(const result_t *r, const char *layout, int workers, int repetitions, int first) {
    printf("%s{\"layout\":\"%s\",\"method\":\"%s\",\"requested_workers\":%d,\"actual_threads_min\":%d,\"actual_threads_max\":%d,\"correct_runs\":%d,\"repetitions\":%d,\"median_wall_ns\":%.3f,\"median_process_cpu_ns\":%.3f,\"median_cpu_wall_ratio\":%.9f,\"speedup_vs_matching_serial\":%.9f,\"wall_samples_ns\":[",
        first ? "" : ",", layout, r->name, workers, r->actual_min, r->actual_max, r->correct_runs, repetitions,
        r->median_wall_ns, r->median_cpu_ns, r->median_wall_ns > 0 ? r->median_cpu_ns / r->median_wall_ns : 0.0, r->speedup);
    for (int i = 0; i < repetitions; ++i) printf("%s%.0f", i ? "," : "", r->wall_samples[i]);
    printf("],\"process_cpu_samples_ns\":[");
    for (int i = 0; i < repetitions; ++i) printf("%s%.0f", i ? "," : "", r->cpu_samples[i]);
    printf("]}");
}
int main(int argc, char **argv) {
    long long repeats = 250000; int workers[MAX_WORKERS] = {1,2,4,8}, worker_count = 4;
    int warmups = 1, repetitions = 5;
    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "--repeat-count") && i + 1 < argc) {
            if (!parse_positive(argv[++i], &repeats) || repeats > 1000000000000LL) return 2;
        } else if (!strcmp(argv[i], "--workers") && i + 1 < argc) {
            if (!parse_workers(argv[++i], workers, &worker_count)) return 2;
        } else if (!strcmp(argv[i], "--warmups") && i + 1 < argc) {
            if (!parse_nonnegative(argv[++i], &warmups)) return 2;
        } else if (!strcmp(argv[i], "--repetitions") && i + 1 < argc) {
            if (!parse_nonnegative(argv[++i], &repetitions) || repetitions < 1) return 2;
        } else { fprintf(stderr, "unknown argument: %s\n", argv[i]); return 2; }
    }
    omp_set_dynamic(0);
    if (!exact_accumulator_self_test()) { fprintf(stderr, "exact accumulator self-test failed\n"); return 3; }
    const char *layouts[] = {"triplet_order", "grouped_cancellation"};
    const method_t serial_methods[] = {SERIAL_NAIVE,SERIAL_LONG_DOUBLE,SERIAL_PAIRWISE,SERIAL_NEUMAIER,SERIAL_EXACT};
    const method_t parallel_methods[] = {OMP_NAIVE,OMP_LONG_DOUBLE,OMP_PAIRWISE,OMP_NEUMAIER,OMP_EXACT};
    const int cases_expected = 2 * (5 + 5 * worker_count);
    printf("{\"study_id\":\"NOEMA-2026-005\",\"experiment_id\":\"NOEMA-2026-005-NATIVE-ACCUMULATORS-001\",\"exact_accumulator_self_test_passed\":true,\"repeat_count\":%lld,\"warmups\":%d,\"repetitions\":%d,\"workers\":[", repeats, warmups, repetitions);
    for (int i = 0; i < worker_count; ++i) printf("%s%d", i ? "," : "", workers[i]);
    printf("],\"cases_expected\":%d,\"long_double_mant_dig\":%d,\"sizeof_long_double\":%zu,\"openmp_version\":%d,\"cpu_count\":%d,\"cases\":[", cases_expected, LDBL_MANT_DIG, sizeof(long double), _OPENMP, omp_get_num_procs());
    int first = 1;
    for (int l = 0; l < 2; ++l) {
        double baselines[5] = {0};
        result_t serial_results[5];
        for (int m = 0; m < 5; ++m) {
            serial_results[m] = measure(repeats, (layout_t)l, serial_methods[m], 1, warmups, repetitions, 1.0);
            baselines[m] = serial_results[m].median_wall_ns;
            print_case(&serial_results[m], layouts[l], 1, repetitions, first); first = 0;
            free(serial_results[m].wall_samples); free(serial_results[m].cpu_samples);
        }
        for (int m = 0; m < 5; ++m) {
            int baseline_index = (int)serial_baseline(parallel_methods[m]);
            double baseline = baselines[baseline_index];
            for (int w = 0; w < worker_count; ++w) {
                result_t r = measure(repeats, (layout_t)l, parallel_methods[m], workers[w], warmups, repetitions, baseline);
                print_case(&r, layouts[l], workers[w], repetitions, first); first = 0;
                free(r.wall_samples); free(r.cpu_samples);
            }
        }
    }
    struct rusage usage; memset(&usage, 0, sizeof(usage)); getrusage(RUSAGE_SELF, &usage);
#ifdef __APPLE__
    const char *rss_unit = "bytes";
#else
    const char *rss_unit = "KiB";
#endif
    printf("],\"process_peak_rss\":%ld,\"process_peak_rss_unit\":\"%s\"}\n", usage.ru_maxrss, rss_unit);
    return 0;
}
