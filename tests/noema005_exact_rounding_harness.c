#define main noema_native_benchmark_main
#include "../scripts/noema005_native_accumulator_benchmark.c"
#undef main

static int parse_decimal_accumulator(const char *text, exact_accum_t *value) {
    memset(value, 0, sizeof(*value));
    int negative = 0;
    if (*text == '-') {
        negative = 1;
        ++text;
    }
    if (!*text) return 0;

    for (const char *cursor = text; *cursor; ++cursor) {
        if (*cursor < '0' || *cursor > '9') return 0;
        uint64_t carry = (uint64_t)(*cursor - '0');
        for (int limb = 0; limb < EXACT_LIMBS; ++limb) {
            __uint128_t product = (__uint128_t)value->limb[limb] * 10 + carry;
            value->limb[limb] = (uint64_t)product;
            carry = (uint64_t)(product >> 64);
        }
        if (carry) return 0;
    }

    if (negative) {
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
    while (fgets(line, sizeof(line), stdin)) {
        line[strcspn(line, "\r\n")] = '\0';
        if (!*line) continue;

        exact_accum_t value;
        if (!parse_decimal_accumulator(line, &value)) {
            fprintf(stderr, "invalid or out-of-range exact integer input\n");
            return 2;
        }

        double rounded = exact_to_binary64(&value);
        uint64_t bits = 0;
        memcpy(&bits, &rounded, sizeof(bits));
        printf("%016" PRIx64 "\n", bits);
    }
    return ferror(stdin) ? 3 : 0;
}
