#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <float.h>
#include <math.h>
#include <inttypes.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <time.h>

typedef enum { TRIPLET, GROUPED } layout_t;
typedef enum { NAIVE, NEUMAIER, LONG_DOUBLE, PAIRWISE } method_t;

typedef struct {
    const char *layout;
    const char *method;
    int requested_workers;
    int actual_threads_min;
    int actual_threads_max;
    int correct_runs;
    int repetitions;
    double median_wall_ns;
    double median_process_cpu_ns;
    double speedup_vs_serial_method;
    double median_effective_input_gib_s;
    double *wall_samples;
    double *cpu_samples;
} result_t;

static double now_ns(clockid_t id) {
    struct timespec ts;
    if (clock_gettime(id, &ts) != 0) { perror("clock_gettime"); exit(2); }
    return (double)ts.tv_sec * 1e9 + (double)ts.tv_nsec;
}

static void add_neumaier(double x, double *sum, double *corr) {
    double t = *sum + x;
    if (fabs(*sum) >= fabs(x)) *corr += (*sum - t) + x;
    else *corr += (x - t) + *sum;
    *sum = t;
}

static double pairwise_sum(const double *a, size_t lo, size_t hi) {
    size_t n = hi - lo;
    if (n <= 1024) {
        double sum = 0.0;
        for (size_t i = lo; i < hi; ++i) sum += a[i];
        return sum;
    }
    size_t mid = lo + n / 2;
    return pairwise_sum(a, lo, mid) + pairwise_sum(a, mid, hi);
}

static double serial_double(const double *a, size_t n, method_t method) {
    double sum = 0.0, corr = 0.0;
    if (method == PAIRWISE) return pairwise_sum(a, 0, n);
    for (size_t i = 0; i < n; ++i) {
        if (method == NEUMAIER) add_neumaier(a[i], &sum, &corr);
        else sum += a[i];
    }
    return method == NEUMAIER ? sum + corr : sum;
}

static long double serial_long_double(const double *a, size_t n) {
    long double sum = 0.0L;
    for (size_t i = 0; i < n; ++i) sum += (long double)a[i];
    return sum;
}

static double parallel_double(const double *a, size_t n, method_t method,
                              int workers, int *actual_threads) {
    double *sums = calloc((size_t)workers, sizeof(*sums));
    double *corrs = calloc((size_t)workers, sizeof(*corrs));
    if (!sums || !corrs) { fprintf(stderr, "allocation failed\n"); exit(2); }
    int actual = 0;
#pragma omp parallel num_threads(workers) shared(actual, sums, corrs)
    {
        int tid = omp_get_thread_num();
        int team = omp_get_num_threads();
        size_t begin = n * (size_t)tid / (size_t)team;
        size_t end = n * (size_t)(tid + 1) / (size_t)team;
        double local = 0.0, correction = 0.0;
#pragma omp single
        actual = team;
        if (method == PAIRWISE) local = pairwise_sum(a, begin, end);
        else {
            for (size_t i = begin; i < end; ++i) {
                if (method == NEUMAIER) add_neumaier(a[i], &local, &correction);
                else local += a[i];
            }
        }
        sums[tid] = local;
        corrs[tid] = correction;
    }
    *actual_threads = actual;
    double result = 0.0, correction = 0.0;
    if (method == PAIRWISE) result = pairwise_sum(sums, 0, (size_t)actual);
    else if (method == NEUMAIER) {
        for (int i = 0; i < actual; ++i) {
            add_neumaier(sums[i], &result, &correction);
            add_neumaier(corrs[i], &result, &correction);
        }
        result += correction;
    } else {
        for (int i = 0; i < actual; ++i) result += sums[i];
    }
    free(sums); free(corrs);
    return result;
}

static long double parallel_long_double(const double *a, size_t n, int workers,
                                        int *actual_threads) {
    long double *partials = calloc((size_t)workers, sizeof(*partials));
    if (!partials) { fprintf(stderr, "allocation failed\n"); exit(2); }
    int actual = 0;
#pragma omp parallel num_threads(workers) shared(actual, partials)
    {
        int tid = omp_get_thread_num();
        int team = omp_get_num_threads();
        size_t begin = n * (size_t)tid / (size_t)team;
        size_t end = n * (size_t)(tid + 1) / (size_t)team;
        long double local = 0.0L;
#pragma omp single
        actual = team;
        for (size_t i = begin; i < end; ++i) local += (long double)a[i];
        partials[tid] = local;
    }
    *actual_threads = actual;
    long double result = 0.0L;
    for (int i = 0; i < actual; ++i) result += partials[i];
    free(partials);
    return result;
}

static int cmp_double(const void *x, const void *y) {
    double a = *(const double *)x, b = *(const double *)y;
    return (a > b) - (a < b);
}

static double median(const double *values, int n) {
    double *copy = malloc((size_t)n * sizeof(*copy));
    if (!copy) { fprintf(stderr, "median allocation failed\n"); exit(2); }
    memcpy(copy, values, (size_t)n * sizeof(*copy));
    qsort(copy, (size_t)n, sizeof(*copy), cmp_double);
    double result = n % 2 ? copy[n / 2] : (copy[n / 2 - 1] + copy[n / 2]) / 2.0;
    free(copy);
    return result;
}

static const char *method_name(method_t m, int parallel) {
    if (m == NAIVE) return parallel ? "openmp_naive_partials" : "serial_naive";
    if (m == NEUMAIER) return parallel ? "openmp_neumaier_full_state" : "serial_neumaier";
    if (m == LONG_DOUBLE) return parallel ? "openmp_long_double_partials" : "serial_long_double";
    return parallel ? "openmp_pairwise_partials" : "serial_pairwise";
}

static result_t measure(const double *a, size_t n, uint64_t expected, layout_t layout,
                        method_t method, int parallel, int workers,
                        int warmups, int repetitions, double baseline_ns,
                        uint64_t input_bytes) {
    result_t r = {0};
    r.layout = layout == TRIPLET ? "triplet" : "grouped";
    r.method = method_name(method, parallel);
    r.requested_workers = parallel ? workers : 1;
    r.actual_threads_min = 1000000;
    r.actual_threads_max = 0;
    r.repetitions = repetitions;
    r.wall_samples = calloc((size_t)repetitions, sizeof(double));
    r.cpu_samples = calloc((size_t)repetitions, sizeof(double));
    if (!r.wall_samples || !r.cpu_samples) { fprintf(stderr, "sample allocation failed\n"); exit(2); }
    for (int run = 0; run < warmups + repetitions; ++run) {
        int actual = 1;
        double wall0 = now_ns(CLOCK_MONOTONIC);
        double cpu0 = now_ns(CLOCK_PROCESS_CPUTIME_ID);
        int correct = 0;
        if (method == LONG_DOUBLE) {
            long double value = parallel ? parallel_long_double(a, n, workers, &actual) : serial_long_double(a, n);
            correct = value == (long double)expected;
        } else {
            double value = parallel ? parallel_double(a, n, method, workers, &actual) : serial_double(a, n, method);
            correct = value == (double)expected;
        }
        double cpu = now_ns(CLOCK_PROCESS_CPUTIME_ID) - cpu0;
        double wall = now_ns(CLOCK_MONOTONIC) - wall0;
        if (run >= warmups) {
            int slot = run - warmups;
            r.wall_samples[slot] = wall;
            r.cpu_samples[slot] = cpu;
            r.correct_runs += correct;
            if (actual < r.actual_threads_min) r.actual_threads_min = actual;
            if (actual > r.actual_threads_max) r.actual_threads_max = actual;
        }
    }
    r.median_wall_ns = median(r.wall_samples, repetitions);
    r.median_process_cpu_ns = median(r.cpu_samples, repetitions);
    r.speedup_vs_serial_method = baseline_ns > 0.0 ? baseline_ns / r.median_wall_ns : 1.0;
    r.median_effective_input_gib_s = r.median_wall_ns > 0.0
        ? ((double)input_bytes / (1024.0 * 1024.0 * 1024.0)) / (r.median_wall_ns / 1e9) : 0.0;
    return r;
}

static void print_case(const result_t *r, int first) {
    printf("%s{\"layout\":\"%s\",\"method\":\"%s\",\"requested_workers\":%d,"
           "\"actual_threads_min\":%d,\"actual_threads_max\":%d,\"correct_runs\":%d,\"repetitions\":%d,"
           "\"median_wall_ns\":%.0f,\"median_process_cpu_ns\":%.0f,\"speedup_vs_serial_method\":%.9f,"
           "\"median_effective_input_gib_s\":%.9f,\"wall_samples_ns\":[",
           first ? "" : ",", r->layout, r->method, r->requested_workers,
           r->actual_threads_min, r->actual_threads_max, r->correct_runs, r->repetitions,
           r->median_wall_ns, r->median_process_cpu_ns, r->speedup_vs_serial_method,
           r->median_effective_input_gib_s);
    for (int i = 0; i < r->repetitions; ++i) printf("%s%.0f", i ? "," : "", r->wall_samples[i]);
    printf("],\"process_cpu_samples_ns\":[");
    for (int i = 0; i < r->repetitions; ++i) printf("%s%.0f", i ? "," : "", r->cpu_samples[i]);
    printf("]}");
}

int main(int argc, char **argv) {
    size_t repeats = 12000000;
    int workers[] = {1, 2, 4, 5, 8};
    int worker_count = 5, warmups = 1, repetitions = 5;
    if (argc > 1) repeats = (size_t)strtoull(argv[1], NULL, 10);
    if (argc > 2) repetitions = atoi(argv[2]);
    if (argc > 3) warmups = atoi(argv[3]);
    if (repeats < 1000 || repetitions < 3 || warmups < 0) {
        fprintf(stderr, "usage: %s [repeats>=1000] [repetitions>=3] [warmups>=0]\n", argv[0]);
        return 2;
    }
    if (repeats > SIZE_MAX / (3 * sizeof(double))) return 2;
    size_t n = repeats * 3;
    uint64_t input_bytes = (uint64_t)n * sizeof(double);
    double *a = NULL;
    if (posix_memalign((void **)&a, 64, (size_t)input_bytes) != 0 || !a) {
        fprintf(stderr, "input allocation failed for %" PRIu64 " bytes\n", input_bytes);
        return 2;
    }
    const double large = 9007199254740992.0; /* 2^53, exactly representable */
    for (int layout = 0; layout < 2; ++layout) {
        for (size_t i = 0; i < n; ++i) {
            if (layout == TRIPLET) {
                a[i] = i % 3 == 0 ? large : (i % 3 == 1 ? 1.0 : -large);
            } else {
                a[i] = i < repeats ? large : (i < 2 * repeats ? 1.0 : -large);
            }
        }
        struct rusage usage;
        getrusage(RUSAGE_SELF, &usage);
        printf("{\"layout\":\"%s\",\"repeats\":%zu,\"input_elements\":%zu,\"input_bytes\":%" PRIu64 ",\"peak_rss_kib\":%ld,\"warmups\":%d,\"repetitions\":%d,\"long_double_mant_dig\":%d,\"cases\":[",
               layout == TRIPLET ? "triplet" : "grouped", repeats, n, input_bytes,
               usage.ru_maxrss, warmups, repetitions, LDBL_MANT_DIG);
        int first = 1;
        double serial_baselines[4] = {0};
        for (int m = 0; m < 4; ++m) {
            result_t r = measure(a, n, (uint64_t)repeats, (layout_t)layout,
                                 (method_t)m, 0, 1, warmups, repetitions, 0.0, input_bytes);
            serial_baselines[m] = r.median_wall_ns;
            print_case(&r, first); first = 0;
            free(r.wall_samples); free(r.cpu_samples);
        }
        for (int m = 0; m < 4; ++m) {
            for (int w = 0; w < worker_count; ++w) {
                result_t r = measure(a, n, (uint64_t)repeats, (layout_t)layout,
                                     (method_t)m, 1, workers[w], warmups, repetitions,
                                     serial_baselines[m], input_bytes);
                print_case(&r, first); first = 0;
                free(r.wall_samples); free(r.cpu_samples);
            }
        }
        printf("]}\n");
    }
    free(a);
    return 0;
}
