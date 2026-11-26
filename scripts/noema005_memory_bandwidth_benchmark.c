#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <float.h>
#include <math.h>
#include <limits.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <time.h>
#define REP 5
#define WARM 1
#define NW 4
typedef enum { S_NAIVE, S_LONG, S_NEUMAIER, P_NAIVE, P_LONG, P_NEUMAIER } method_t;
typedef struct { const char *name; int workers, actual_min, actual_max, correct; size_t bytes; double wall[REP], cpu[REP], mw, mc, speedup, throughput; } result_t;
static const int worker_values[NW]={1,2,4,8};
static const method_t serial_methods[3]={S_NAIVE,S_LONG,S_NEUMAIER};
static const method_t parallel_methods[3]={P_NAIVE,P_LONG,P_NEUMAIER};
static const char *name_of(method_t m) {
    switch(m){case S_NAIVE:return "serial_naive";case S_LONG:return "serial_long_double";case S_NEUMAIER:return "serial_neumaier";case P_NAIVE:return "openmp_naive_partials";case P_LONG:return "openmp_long_double";default:return "openmp_neumaier_state";}
}
static void add_neumaier(double x,double *s,double *c){double t=*s+x;if(fabs(*s)>=fabs(x))*c+=(*s-t)+x;else *c+=(x-t)+*s;*s=t;}
static double now_ns(clockid_t id){struct timespec ts;if(clock_gettime(id,&ts)!=0){perror("clock_gettime");exit(2);}return (double)ts.tv_sec*1e9+(double)ts.tv_nsec;}
static int cmp(const void *a,const void *b){double x=*(const double*)a,y=*(const double*)b;return (x>y)-(x<y);}
static double median(const double *v){double c[REP];memcpy(c,v,sizeof(c));qsort(c,REP,sizeof(double),cmp);return c[REP/2];}
static double serial_sum(const double *v,long long n,method_t m){
    if(m==S_LONG){long double s=0.0L;for(long long i=0;i<n;++i)s+=(long double)v[i];return (double)s;}
    double s=0.0,c=0.0;for(long long i=0;i<n;++i){if(m==S_NEUMAIER)add_neumaier(v[i],&s,&c);else s+=v[i];}
    return m==S_NEUMAIER?s+c:s;
}
static double parallel_sum(const double *v,long long n,method_t m,int requested,int *actual){
    double *sums=calloc((size_t)requested,sizeof(double)),*corr=calloc((size_t)requested,sizeof(double));
    long double *longs=calloc((size_t)requested,sizeof(long double));
    if(!sums||!corr||!longs){fprintf(stderr,"state allocation failed\n");exit(2);}
#pragma omp parallel num_threads(requested) shared(actual,sums,corr,longs)
    {
        int tid=omp_get_thread_num();double s=0.0,c=0.0;long double ls=0.0L;
#pragma omp single
        *actual=omp_get_num_threads();
#pragma omp for schedule(static)
        for(long long i=0;i<n;++i){if(m==P_NEUMAIER)add_neumaier(v[i],&s,&c);else if(m==P_LONG)ls+=(long double)v[i];else s+=v[i];}
        sums[tid]=s;corr[tid]=c;longs[tid]=ls;
    }
    double result=0.0,correction=0.0;long double long_result=0.0L;
    for(int i=0;i<*actual;++i){if(m==P_NEUMAIER){add_neumaier(sums[i],&result,&correction);add_neumaier(corr[i],&result,&correction);}else if(m==P_LONG)long_result+=longs[i];else result+=sums[i];}
    free(sums);free(corr);free(longs);
    if(m==P_NEUMAIER) return result+correction;
    if(m==P_LONG) return (double)long_result;
    return result;
}
static double run_once(const double *v,long long n,method_t m,int workers,int *actual){if(m<=S_NEUMAIER){*actual=1;return serial_sum(v,n,m);}return parallel_sum(v,n,m,workers,actual);}
static result_t measure(const double *v,long long n,size_t bytes,long long expected,method_t m,int workers,double baseline){
    result_t r={0};r.name=name_of(m);r.workers=workers;r.bytes=bytes;r.actual_min=256;
    for(int i=0;i<WARM+REP;++i){int actual=1;double c0=now_ns(CLOCK_PROCESS_CPUTIME_ID),w0=now_ns(CLOCK_MONOTONIC);double value=run_once(v,n,m,workers,&actual);double wall=now_ns(CLOCK_MONOTONIC)-w0,cpu=now_ns(CLOCK_PROCESS_CPUTIME_ID)-c0;
        if(i>=WARM){int k=i-WARM;r.wall[k]=wall;r.cpu[k]=cpu;r.correct+=(value==(double)expected);if(actual<r.actual_min)r.actual_min=actual;if(actual>r.actual_max)r.actual_max=actual;}}
    r.mw=median(r.wall);r.mc=median(r.cpu);r.speedup=baseline>0?baseline/r.mw:1.0;r.throughput=(double)bytes/r.mw;return r;
}
static void print_case(const result_t *r,int first){
    printf("%s{\"method\":\"%s\",\"requested_workers\":%d,\"actual_threads_min\":%d,\"actual_threads_max\":%d,\"correct_runs\":%d,\"runs\":%d,\"median_wall_ns\":%.0f,\"median_process_cpu_ns\":%.0f,\"speedup_vs_matching_serial\":%.9f,\"effective_read_gb_s\":%.9f,\"bytes_read_per_run\":%zu,\"wall_samples_ns\":[",first?"":",",r->name,r->workers,r->actual_min,r->actual_max,r->correct,REP,r->mw,r->mc,r->speedup,r->throughput,r->bytes);
    for(int i=0;i<REP;++i) printf("%s%.0f",i?",":"",r->wall[i]);
    printf("],\"process_cpu_samples_ns\":[");
    for(int i=0;i<REP;++i) printf("%s%.0f",i?",":"",r->cpu[i]);
    printf("]}");
}
int main(int argc,char **argv){
    long long repeat=4194304LL;
    if(argc>2){fprintf(stderr,"Usage: %s [repeat-count]\n",argv[0]);return 2;}
    if(argc==2){char *end=NULL;errno=0;repeat=strtoll(argv[1],&end,10);if(errno||!end||*end||repeat<8){fprintf(stderr,"invalid repeat-count\n");return 2;}}
    if(repeat%8||repeat>9007199254740992LL||repeat>LLONG_MAX/3||repeat>(long long)(SIZE_MAX/(3*sizeof(double)))){fprintf(stderr,"repeat-count must be <=2^53, divisible by 8 and fit address space\n");return 2;}
    long long n=3*repeat;size_t bytes=(size_t)n*sizeof(double);double *values=NULL;
    if(posix_memalign((void**)&values,64,bytes)!=0||!values){fprintf(stderr,"input allocation failed for %zu bytes\n",bytes);return 2;}
    const double large=9007199254740992.0;for(long long i=0;i<n;++i)values[i]=(i%3==0)?large:(i%3==1)?1.0:-large;
    omp_set_dynamic(0);result_t results[15];double baseline[3]={0};int total=0;
    for(int i=0;i<3;++i){results[total]=measure(values,n,bytes,repeat,serial_methods[i],1,0);baseline[i]=results[total].mw;++total;}
    for(int w=0;w<NW;++w)for(int m=0;m<3;++m){int b=(int)(parallel_methods[m]-P_NAIVE);results[total++]=measure(values,n,bytes,repeat,parallel_methods[m],worker_values[w],baseline[b]);}
    struct rusage ru;long rss=-1;if(getrusage(RUSAGE_SELF,&ru)==0)rss=ru.ru_maxrss;
    printf("{\"study_id\":\"NOEMA-2026-005\",\"experiment_id\":\"NOEMA-2026-005-MEMORY-001\",\"status\":\"synthetic_memory_backed_reduction\",\"methodology\":\"One aligned binary64 array is allocated once and reused. Effective input throughput includes algorithm and runtime overhead and is not a hardware DRAM-bandwidth claim.\",\"environment\":{\"openmp_version\":%d,\"processors\":%d,\"double_mant_dig\":%d,\"long_double_mant_dig\":%d,\"sizeof_double\":%zu,\"sizeof_long_double\":%zu},\"input\":{\"pattern\":[\"2^53\",\"1\",\"-2^53\"],\"repeat_count\":%lld,\"elements\":%lld,\"bytes\":%zu,\"exact_sum\":%lld,\"alignment_bytes\":64},\"workers\":[1,2,4,8],\"warmups\":%d,\"repetitions\":%d,\"cases_expected\":%d,\"process_peak_rss_platform_units\":%ld,\"cases\":[",
#ifdef _OPENMP
    _OPENMP,
#else
    0,
#endif
    omp_get_num_procs(),DBL_MANT_DIG,LDBL_MANT_DIG,sizeof(double),sizeof(long double),repeat,n,bytes,repeat,WARM,REP,total,rss);
    for(int i=0;i<total;++i)print_case(&results[i],i==0);printf("]}\n");free(values);return 0;
}
