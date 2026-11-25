
#include <stddef.h>
#include <math.h>

void noema_naive_sum(const double *values, size_t n, ptrdiff_t stride, double *result) {
    double total = 0.0;
    for (size_t i = 0; i < n; ++i) {
        total += values[(ptrdiff_t)i * stride];
    }
    *result = total;
}

void noema_neumaier_state(const double *values, size_t n, ptrdiff_t stride,
                          double *sum_out, double *correction_out) {
    double total = 0.0;
    double correction = 0.0;
    for (size_t i = 0; i < n; ++i) {
        const double value = values[(ptrdiff_t)i * stride];
        const double updated = total + value;
        if (fabs(total) >= fabs(value)) {
            correction += (total - updated) + value;
        } else {
            correction += (value - updated) + total;
        }
        total = updated;
    }
    *sum_out = total;
    *correction_out = correction;
}
