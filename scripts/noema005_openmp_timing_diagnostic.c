#define _GNU_SOURCE
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <inttypes.h>
#include <omp.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <time.h>
#include <unistd.h>
#define MAX_WORKERS 256

typedef struct {
    int thread_index;
    uint64_t cpu_ns;
    uint64_t rusage_thread_ns;
    int thread_cgroup_matches_process;
    int affinity_cpu_count;
    char affinity_cpus[2048];
    int cpu_start;
    int cpu_end;
    double checksum;
} thread_sample_t;

static uint64_t timespec_ns(const struct timespec *value) {
    return (uint64_t)value->tv_sec * UINT64_C(1000000000) + (uint64_t)value->tv_nsec;
}
static uint64_t clock_ns(clockid_t clock_id) {
    struct timespec value;
    if (clock_gettime(clock_id, &value) != 0) { perror("clock_gettime"); exit(2); }
    return timespec_ns(&value);
}
static uint64_t rusage_thread_ns(const struct rusage *value) {
    uint64_t user = (uint64_t)value->ru_utime.tv_sec * UINT64_C(1000000000) + (uint64_t)value->ru_utime.tv_usec * UINT64_C(1000);
    uint64_t system = (uint64_t)value->ru_stime.tv_sec * UINT64_C(1000000000) + (uint64_t)value->ru_stime.tv_usec * UINT64_C(1000);
    return user + system;
}
static int read_unified_cgroup(const char *path, char *buffer, size_t capacity) {
    FILE *file = fopen(path, "r");
    if (!file) return -1;
    char line[4096];
    while (fgets(line, sizeof(line), file)) {
        if (strncmp(line, "0::", 3) != 0) continue;
        size_t length = strcspn(line + 3, "\r\n");
        if (length + 1 > capacity) { fclose(file); return -1; }
        memcpy(buffer, line + 3, length);
        buffer[length] = '\0';
        fclose(file);
        return 1;
    }
    fclose(file);
    return -1;
}
static int thread_cgroup_matches_process(void) {
    char process_cgroup[4096] = {0};
    char thread_cgroup[4096] = {0};
    if (read_unified_cgroup("/proc/self/cgroup", process_cgroup, sizeof(process_cgroup)) != 1) return -1;
    if (read_unified_cgroup("/proc/thread-self/cgroup", thread_cgroup, sizeof(thread_cgroup)) != 1) return -1;
    return strcmp(process_cgroup, thread_cgroup) == 0 ? 1 : 0;
}
static int affinity_string(char *buffer, size_t capacity) {
    cpu_set_t mask;
    if (sched_getaffinity(0, sizeof(mask), &mask) != 0) return -1;
    size_t used = 0;
    int count = 0;
    for (int cpu = 0; cpu < CPU_SETSIZE; ++cpu) {
        if (!CPU_ISSET(cpu, &mask)) continue;
        int written = snprintf(buffer + used, capacity - used, "%s%d", count ? "," : "", cpu);
        if (written < 0 || (size_t)written >= capacity - used) return -1;
        used += (size_t)written;
        count++;
    }
    buffer[used] = '\0';
    return count;
}
static int parse_positive(const char *text, long long *out) {
    char *end = NULL; errno = 0;
    long long value = strtoll(text, &end, 10);
    if (errno || !end || *end != '\0' || value < 1) return 0;
    *out = value; return 1;
}
static int parse_workers(const char *text, int out[MAX_WORKERS], int *count) {
    char *copy = strdup(text); if (!copy) return 0;
    int n = 0; char *save = NULL;
    for (char *token = strtok_r(copy, ",", &save); token; token = strtok_r(NULL, ",", &save)) {
        long long value = 0;
        if (!parse_positive(token, &value) || value > MAX_WORKERS || n >= MAX_WORKERS) { free(copy); return 0; }
        for (int i = 0; i < n; ++i) if (out[i] == (int)value) { free(copy); return 0; }
        out[n++] = (int)value;
    }
    free(copy); *count = n; return n > 0;
}
static void run_once(int requested_workers, long long work_items, int repetition, int emit) {
    thread_sample_t *samples = calloc((size_t)requested_workers, sizeof(*samples));
    double *partials = calloc((size_t)requested_workers, sizeof(*partials));
    if (!samples || !partials) { fprintf(stderr, "allocation failed\n"); exit(2); }
    int actual_threads = 0;
    uint64_t wall_start = clock_ns(CLOCK_MONOTONIC);
    uint64_t process_start = clock_ns(CLOCK_PROCESS_CPUTIME_ID);
    double omp_start = omp_get_wtime();
#pragma omp parallel num_threads(requested_workers) shared(actual_threads, samples, partials)
    {
        int tid = omp_get_thread_num();
        thread_sample_t *sample = &samples[tid];
        struct rusage usage_start, usage_end;
        uint64_t thread_start = clock_ns(CLOCK_THREAD_CPUTIME_ID);
        if (getrusage(RUSAGE_THREAD, &usage_start) != 0) { perror("getrusage start"); exit(2); }
        sample->thread_index = tid;
        sample->thread_cgroup_matches_process = thread_cgroup_matches_process();
        sample->cpu_start = sched_getcpu();
        sample->affinity_cpu_count = affinity_string(sample->affinity_cpus, sizeof(sample->affinity_cpus));
        if (sample->affinity_cpu_count < 1) { fprintf(stderr, "sched_getaffinity failed or returned an empty mask\n"); exit(2); }
#pragma omp single
        actual_threads = omp_get_num_threads();
        double accumulator = 1.0 + (double)tid * 0.125;
#pragma omp for schedule(static)
        for (long long i = 0; i < work_items; ++i) {
            double term = (double)(((uint64_t)i + (uint64_t)tid * 13u) % 17u + 1u) * 1e-18;
            accumulator = accumulator * 1.0000000000000002 + term;
        }
        partials[tid] = accumulator;
        sample->checksum = accumulator;
        sample->cpu_end = sched_getcpu();
        uint64_t thread_end = clock_ns(CLOCK_THREAD_CPUTIME_ID);
        if (getrusage(RUSAGE_THREAD, &usage_end) != 0) { perror("getrusage end"); exit(2); }
        sample->cpu_ns = thread_end - thread_start;
        sample->rusage_thread_ns = rusage_thread_ns(&usage_end) - rusage_thread_ns(&usage_start);
    }
    double omp_end = omp_get_wtime();
    uint64_t process_end = clock_ns(CLOCK_PROCESS_CPUTIME_ID);
    uint64_t wall_end = clock_ns(CLOCK_MONOTONIC);
    uint64_t wall_ns = wall_end - wall_start;
    uint64_t process_cpu_ns = process_end - process_start;
    uint64_t thread_cpu_sum_ns = 0;
    double checksum = 0.0;
    for (int i = 0; i < actual_threads; ++i) { thread_cpu_sum_ns += samples[i].cpu_ns; checksum += partials[i]; }
    if (emit) {
        printf("{\"requested_workers\":%d,\"actual_threads\":%d,\"repetition\":%d,\"work_items\":%lld,\"wall_ns\":%" PRIu64 ",\"process_cpu_ns\":%" PRIu64 ",\"omp_wall_ns\":%" PRIu64 ",\"process_cpu_wall_ratio\":%.9f,\"thread_cpu_sum_ns\":%" PRIu64 ",\"checksum\":%.17g,\"threads\":[",
               requested_workers, actual_threads, repetition, work_items, wall_ns, process_cpu_ns,
               (uint64_t)((omp_end - omp_start) * 1e9), wall_ns ? (double)process_cpu_ns / (double)wall_ns : 0.0,
               thread_cpu_sum_ns, checksum);
        for (int i = 0; i < actual_threads; ++i) {
            const thread_sample_t *sample = &samples[i];
            if (i) putchar(',');
            printf("{\"thread_index\":%d,\"cpu_ns\":%" PRIu64 ",\"rusage_thread_ns\":%" PRIu64 ",\"thread_cgroup_matches_process\":",
                   sample->thread_index, sample->cpu_ns, sample->rusage_thread_ns);
            if (sample->thread_cgroup_matches_process < 0) printf("null");
            else printf("%s", sample->thread_cgroup_matches_process ? "true" : "false");
            printf(",\"affinity_cpu_count\":%d,\"affinity_cpus\":\"%s\",\"cpu_start\":%d,\"cpu_end\":%d,\"checksum\":%.17g}",
                   sample->affinity_cpu_count, sample->affinity_cpus, sample->cpu_start, sample->cpu_end, sample->checksum);
        }
        puts("]}");
    }
    free(samples); free(partials);
}
int main(int argc, char **argv) {
    int workers[MAX_WORKERS] = {0}, worker_count = 0, repetitions = 20;
    long long work_items = 8000000;
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--workers") == 0 && i + 1 < argc) {
            if (!parse_workers(argv[++i], workers, &worker_count)) { fprintf(stderr, "invalid --workers list\n"); return 2; }
        } else if (strcmp(argv[i], "--repetitions") == 0 && i + 1 < argc) {
            long long value = 0;
            if (!parse_positive(argv[++i], &value) || value > 1000) { fprintf(stderr, "invalid --repetitions\n"); return 2; }
            repetitions = (int)value;
        } else if (strcmp(argv[i], "--work-items") == 0 && i + 1 < argc) {
            if (!parse_positive(argv[++i], &work_items)) { fprintf(stderr, "invalid --work-items\n"); return 2; }
        } else { fprintf(stderr, "Usage: %s [--workers 1,2,4,8] [--repetitions 20] [--work-items 8000000]\n", argv[0]); return 2; }
    }
    if (!worker_count && !parse_workers("1,2,4,8", workers, &worker_count)) return 2;
    omp_set_dynamic(0);
    for (int w = 0; w < worker_count; ++w) {
        omp_set_num_threads(workers[w]);
        run_once(workers[w], work_items, 0, 0);
        for (int repetition = 1; repetition <= repetitions; ++repetition) run_once(workers[w], work_items, repetition, 1);
    }
    return 0;
}
