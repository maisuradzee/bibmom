#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <float.h>
#include <inttypes.h>
#include <limits.h>
#include <math.h>
#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <time.h>

#define LARGE_VALUE 9007199254740992.0 /* 2^53, exactly representable in binary64 */
#define MAX_WORKERS 256
#define MAX_REPETITIONS 1000

typedef enum { LAYOUT_TRIPLET, LAYOUT_GROUPED } layout_t;
typedef enum { METHOD_SERIAL_NAIVE, METHOD_SERIAL_NEUMAIER, METHOD_OMP_NAIVE, METHOD_OMP_NEUMAIER } method_t;

typedef struct {
    const char *name;
    double median_wall_ns;
    double median_cpu_ns;
    double speedup;
    int correct_runs;
    int actual_threads_min;
    int actual_threads_max;
    double *wall_samples;
    double *cpu_samples;
} result_t;

static void usage(const char *program) {
    fprintf(stderr, "Usage: %s [--repeat-count N] [--workers 1,2,4,8] [--warmups N] [--repetitions N]\n", program);
}

static int parse_positive(const char *value, long long *out) {
    char *end = NULL;
    errno = 0;
    long long parsed = strtoll(value, &end, 10);
    if (errno || !end || *end != '\0' || parsed < 1) return 0;
    *out = parsed;
    return 1;
}

static int parse_nonnegative(const char *value, int *out) {
    char *end = NULL;
    errno = 0;
    long parsed = strtol(value, &end, 10);
    if (errno || !end || *end != '\0' || parsed < 0 || parsed > MAX_REPETITIONS) return 0;
    *out = (int)parsed;
    return 1;
}

static int parse_workers(const char *value, int workers[], int *count) {
    char *copy = strdup(value);
    if (!copy) return 0;
    int n = 0;
    char *save = NULL;
    for (char *token = strtok_r(copy, ",", &save); token; token = strtok_r(NULL, ",", &save)) {
        long long parsed = 0;
        if (!parse_positive(token, &parsed) || parsed > MAX_WORKERS || n >= MAX_WORKERS) {
            free(copy);
            return 0;
        }
        for (int i = 0; i < n; ++i) {
            if (workers[i] == (int)parsed) { free(copy); return 0; }
        }
        workers[n++] = (int)parsed;
    }
    free(copy);
    *count = n;
    return n > 0;
}

static double value_at(long long index, long long repeat_count, layout_t layout) {
    if (layout == LAYOUT_TRIPLET) {
        switch (index % 3) {
            case 0: return LARGE_VALUE;
            case 1: return 1.0;
            default: return -LARGE_VALUE;
        }
    }
    if (index < repeat_count) return LARGE_VALUE;
    if (index < 2 * repeat_count) return 1.0;
    return -LARGE_VALUE;
}

static void neumaier_add(double value, double *sum, double *correction) {
    double updated = *sum + value;
    if (fabs(*sum) >= fabs(value))
        *correction += (*sum - updated) + value;
    else
        *correction += (value - updated) + *sum;
    *sum = updated;
}

static double serial_compute(long long repeat_count, layout_t layout, method_t method) {
    long long count = 3 * repeat_count;
    double sum = 0.0, correction = 0.0;
    for (long long i = 0; i < count; ++i) {
        double value = value_at(i, repeat_count, layout);
        if (method == METHOD_SERIAL_NEUMAIER) neumaier_add(value, &sum, &correction);
        else sum += value;
    }
    return method == METHOD_SERIAL_NEUMAIER ? sum + correction : sum;
}

static double openmp_compute(long long repeat_count, layout_t layout, method_t method,
                             int requested_workers, int *actual_workers) {
    long long count = 3 * repeat_count;
    double *sums = calloc((size_t)requested_workers, sizeof(double));
    double *corrections = calloc((size_t)requested_workers, sizeof(double));
    if (!sums || !corrections) {
        free(sums); free(corrections);
        fprintf(stderr, "allocation failed for %d worker states\n", requested_workers);
        exit(2);
    }
    int actual = 0;
#pragma omp parallel num_threads(requested_workers) shared(actual, sums, corrections)
    {
        int tid = omp_get_thread_num();
        double local_sum = 0.0, local_correction = 0.0;
#pragma omp single
        actual = omp_get_num_threads();
#pragma omp for schedule(static)
        for (long long i = 0; i < count; ++i) {
            double value = value_at(i, repeat_count, layout);
            if (method == METHOD_OMP_NEUMAIER)
                neumaier_add(value, &local_sum, &local_correction);
            else
                local_sum += value;
        }
        sums[tid] = local_sum;
        corrections[tid] = local_correction;
    }
    *actual_workers = actual;
    double result = 0.0, correction = 0.0;
    for (int i = 0; i < actual; ++i) {
        if (method == METHOD_OMP_NEUMAIER) {
            neumaier_add(sums[i], &result, &correction);
            neumaier_add(corrections[i], &result, &correction);
        } else {
            result += sums[i];
        }
    }
    free(sums);
    free(corrections);
    return method == METHOD_OMP_NEUMAIER ? result + correction : result;
}

static double clock_ns(clockid_t clock_id) {
    struct timespec ts;
    if (clock_gettime(clock_id, &ts) != 0) {
        perror("clock_gettime");
        exit(2);
    }
    return (double)ts.tv_sec * 1e9 + (double)ts.tv_nsec;
}

static int compare_double(const void *left, const void *right) {
    double a = *(const double *)left, b = *(const double *)right;
    return (a > b) - (a < b);
}

static double median(double *values, int count) {
    qsort(values, (size_t)count, sizeof(double), compare_double);
    if (count % 2) return values[count / 2];
    return (values[count / 2 - 1] + values[count / 2]) / 2.0;
}

static result_t measure_case(long long repeat_count, layout_t layout, method_t method,
                             int workers, int warmups, int repetitions, double baseline_ns) {
    result_t result = {0};
    result.wall_samples = calloc((size_t)repetitions, sizeof(double));
    result.cpu_samples = calloc((size_t)repetitions, sizeof(double));
    if (!result.wall_samples || !result.cpu_samples) {
        fprintf(stderr, "sample allocation failed\n"); exit(2);
    }
    result.actual_threads_min = MAX_WORKERS;
    result.actual_threads_max = 0;
    int actual = 1;
    for (int i = 0; i < warmups + repetitions; ++i) {
        double cpu_start = clock_ns(CLOCK_PROCESS_CPUTIME_ID);
        double wall_start = clock_ns(CLOCK_MONOTONIC);
        double value = (method == METHOD_SERIAL_NAIVE || method == METHOD_SERIAL_NEUMAIER)
            ? serial_compute(repeat_count, layout, method)
            : openmp_compute(repeat_count, layout, method, workers, &actual);
        double wall_elapsed = clock_ns(CLOCK_MONOTONIC) - wall_start;
        double cpu_elapsed = clock_ns(CLOCK_PROCESS_CPUTIME_ID) - cpu_start;
        if (i >= warmups) {
            int slot = i - warmups;
            result.wall_samples[slot] = wall_elapsed;
            result.cpu_samples[slot] = cpu_elapsed;
            result.correct_runs += (value == (double)repeat_count);
            if (actual < result.actual_threads_min) result.actual_threads_min = actual;
            if (actual > result.actual_threads_max) result.actual_threads_max = actual;
        }
    }
    double *wall_copy = calloc((size_t)repetitions, sizeof(double));
    double *cpu_copy = calloc((size_t)repetitions, sizeof(double));
    if (!wall_copy || !cpu_copy) { fprintf(stderr, "median allocation failed\n"); exit(2); }
    memcpy(wall_copy, result.wall_samples, (size_t)repetitions * sizeof(double));
    memcpy(cpu_copy, result.cpu_samples, (size_t)repetitions * sizeof(double));
    result.median_wall_ns = median(wall_copy, repetitions);
    result.median_cpu_ns = median(cpu_copy, repetitions);
    result.speedup = baseline_ns > 0.0 ? baseline_ns / result.median_wall_ns : 1.0;
    free(wall_copy); free(cpu_copy);
    if (method == METHOD_SERIAL_NAIVE) result.name = "serial_naive";
    else if (method == METHOD_SERIAL_NEUMAIER) result.name = "serial_neumaier";
    else if (method == METHOD_OMP_NAIVE) result.name = "openmp_naive_partials";
    else result.name = "openmp_neumaier_state";
    return result;
}

static void print_result(const result_t *r, const char *layout, int workers, int repetitions,
                         int first) {
    printf("%s{\"layout\":\"%s\",\"method\":\"%s\",\"requested_workers\":%d,"
           "\"actual_threads_min\":%d,\"actual_threads_max\":%d,\"median_wall_ns\":%.0f,"
           "\"median_process_cpu_ns\":%.0f,\"median_cpu_wall_ratio\":%.9f,\"speedup_vs_matching_serial\":%.9f,"
           "\"correctly_rounded_runs\":%d,\"runs\":%d,\"wall_samples_ns\":[",
           first ? "" : ",", layout, r->name, workers, r->actual_threads_min,
           r->actual_threads_max, r->median_wall_ns, r->median_cpu_ns,
           r->median_wall_ns > 0.0 ? r->median_cpu_ns / r->median_wall_ns : 0.0,
           r->speedup, r->correct_runs, repetitions);
    for (int i = 0; i < repetitions; ++i) printf("%s%.0f", i ? "," : "", r->wall_samples[i]);
    printf("],\"process_cpu_samples_ns\":[");
    for (int i = 0; i < repetitions; ++i) printf("%s%.0f", i ? "," : "", r->cpu_samples[i]);
    printf("]}");
}

int main(int argc, char **argv) {
    long long repeat_count = 250000;
    int workers[MAX_WORKERS] = {1, 2, 4, 8}, worker_count = 4;
    int warmups = 1, repetitions = 5;
    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "--repeat-count") && i + 1 < argc) {
            if (!parse_positive(argv[++i], &repeat_count) || repeat_count > 9007199254740992LL) {
                usage(argv[0]); return 2;
            }
        } else if (!strcmp(argv[i], "--workers") && i + 1 < argc) {
            if (!parse_workers(argv[++i], workers, &worker_count)) { usage(argv[0]); return 2; }
        } else if (!strcmp(argv[i], "--warmups") && i + 1 < argc) {
            if (!parse_nonnegative(argv[++i], &warmups)) { usage(argv[0]); return 2; }
        } else if (!strcmp(argv[i], "--repetitions") && i + 1 < argc) {
            if (!parse_nonnegative(argv[++i], &repetitions) || repetitions < 1) { usage(argv[0]); return 2; }
        } else { usage(argv[0]); return 2; }
    }
    omp_set_dynamic(0);
    if (repeat_count > LLONG_MAX / 3) return 2;
    int cases = 0;
    for (int layout = 0; layout < 2; ++layout) cases += 2 + worker_count * 2;
    printf("{\"study_id\":\"NOEMA-2026-005\",\"experiment_id\":\"NOEMA-2026-005-OPENMP-001\","
           "\"status\":\"synthetic_native_openmp_benchmark\",\"methodology\":\"Generated binary64 cancellation inputs; exact expected sum is repeat_count; process CPU time and monotonic wall time measured separately.\","
           "\"environment\":{\"openmp_version\":%d,\"processors\":%d,\"double_mant_dig\":%d,\"long_double_mant_dig\":%d,\"sizeof_double\":%zu,\"sizeof_long_double\":%zu},"
           "\"input\":{\"repeat_count\":%lld,\"elements_per_layout\":%lld,\"exact_sum\":%lld,\"input_storage_bytes\":0,\"layouts\":[\"triplet_order\",\"grouped_cancellation\"]},"
           "\"warmups\":%d,\"repetitions\":%d,\"cases_expected\":%d,\"cases\":[",
#ifdef _OPENMP
           _OPENMP,
#else
           0,
#endif
           omp_get_num_procs(), DBL_MANT_DIG, LDBL_MANT_DIG, sizeof(double), sizeof(long double),
           repeat_count, 3 * repeat_count, repeat_count, warmups, repetitions, cases);
    int first = 1;
    for (int layout_index = 0; layout_index < 2; ++layout_index) {
        layout_t layout = (layout_t)layout_index;
        const char *layout_name = layout == LAYOUT_TRIPLET ? "triplet_order" : "grouped_cancellation";
        result_t serial_naive = measure_case(repeat_count, layout, METHOD_SERIAL_NAIVE, 1,
                                             warmups, repetitions, 0.0);
        result_t serial_neumaier = measure_case(repeat_count, layout, METHOD_SERIAL_NEUMAIER, 1,
                                                warmups, repetitions, 0.0);
        print_result(&serial_naive, layout_name, 1, repetitions, first); first = 0;
        print_result(&serial_neumaier, layout_name, 1, repetitions, first);
        free(serial_naive.wall_samples); free(serial_naive.cpu_samples);
        free(serial_neumaier.wall_samples); free(serial_neumaier.cpu_samples);
        for (int w = 0; w < worker_count; ++w) {
            int requested = workers[w];
            result_t naive = measure_case(repeat_count, layout, METHOD_OMP_NAIVE, requested,
                                          warmups, repetitions, serial_naive.median_wall_ns);
            result_t compensated = measure_case(repeat_count, layout, METHOD_OMP_NEUMAIER, requested,
                                                 warmups, repetitions, serial_neumaier.median_wall_ns);
            print_result(&naive, layout_name, requested, repetitions, first); first = 0;
            print_result(&compensated, layout_name, requested, repetitions, first);
            free(naive.wall_samples); free(naive.cpu_samples);
            free(compensated.wall_samples); free(compensated.cpu_samples);
        }
    }
    struct rusage usage_stats;
    long peak_rss_kib = -1;
    if (getrusage(RUSAGE_SELF, &usage_stats) == 0) peak_rss_kib = usage_stats.ru_maxrss;
    printf("],\"process_peak_rss_kib\":%ld,\"memory_note\":\"Process-wide high-water mark for the whole benchmark, not per-method allocation; input values are generated on the fly.\"}\n", peak_rss_kib);
    return 0;
}
