#define main noema_native_benchmark_main
#include "../scripts/noema005_native_accumulator_benchmark.c"
#undef main

static exact_accum_t signed_maximum(void) {
    exact_accum_t value;
    for (int i = 0; i < EXACT_LIMBS; ++i) value.limb[i] = UINT64_MAX;
    value.limb[EXACT_LIMBS - 1] = UINT64_MAX >> 1;
    return value;
}

static exact_accum_t signed_minimum(void) {
    exact_accum_t value = {{0}};
    value.limb[EXACT_LIMBS - 1] = UINT64_C(1) << 63;
    return value;
}

static int unchanged_after_failed_add(exact_accum_t *value, int negative) {
    exact_accum_t before = *value;
    int accepted = exact_add_significand_checked(value, 1, 0, negative);
    return !accepted && memcmp(value, &before, sizeof(before)) == 0;
}

int main(void) {
    exact_accum_t value = signed_maximum();
    if (!unchanged_after_failed_add(&value, 0)) return 1;

    value = signed_minimum();
    if (!unchanged_after_failed_add(&value, 1)) return 2;

    value = signed_maximum();
    --value.limb[0];
    if (!exact_add_significand_checked(&value, 1, 0, 0)) return 3;
    exact_accum_t expected_maximum = signed_maximum();
    if (memcmp(&value, &expected_maximum, sizeof(value)) != 0) return 4;

    value = signed_minimum();
    value.limb[0] = 1;
    if (!exact_add_significand_checked(&value, 1, 0, 1)) return 5;
    if (memcmp(&value, &(exact_accum_t){{
        [EXACT_LIMBS - 1] = UINT64_C(1) << 63
    }}, sizeof(value)) != 0) return 6;

    value = signed_maximum();
    exact_accum_t positive_one = {{0}};
    positive_one.limb[0] = 1;
    exact_accum_t before = value;
    if (exact_merge_checked(&value, &positive_one)) return 7;
    if (memcmp(&value, &before, sizeof(value)) != 0) return 8;

    value = signed_minimum();
    exact_accum_t negative_one = {{0}};
    for (int i = 0; i < EXACT_LIMBS; ++i) negative_one.limb[i] = UINT64_MAX;
    before = value;
    if (exact_merge_checked(&value, &negative_one)) return 9;
    if (memcmp(&value, &before, sizeof(value)) != 0) return 10;

    value = signed_maximum();
    if (exact_add_double_checked(&value, DBL_TRUE_MIN)) return 11;
    value = signed_minimum();
    if (exact_add_double_checked(&value, -DBL_TRUE_MIN)) return 12;

    value = (exact_accum_t){{0}};
    if (exact_add_significand_checked(&value, 1, -1, 0)) return 13;
    if (exact_add_double_checked(&value, INFINITY)) return 14;
    if (exact_add_double_checked(&value, NAN)) return 15;

    puts("checked signed accumulator overflow tests passed");
    return 0;
}
