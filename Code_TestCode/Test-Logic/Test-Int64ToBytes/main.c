#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>

// 判断系统是否为小端
static int is_little_endian(void) {
    uint16_t word = 0x0001;
    return *(uint8_t*)&word == 0x01;
}

// 将 int64_t 转换为大端字节数组
void int64_to_big_endian_bytes(int64_t value, uint8_t bytes[8]) {
    if (is_little_endian()) {
        // 小端系统：需要反转字节
        for (int i = 0; i < 8; ++i) {
            bytes[i] = (value >> (56 - i * 8)) & 0xFF;
        }
    } else {
        // 大端系统：直接按内存顺序复制（但为了可移植性，仍使用移位）
        for (int i = 0; i < 8; ++i) {
            bytes[i] = (value >> (56 - i * 8)) & 0xFF;
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s -Int64ToBytes <integer>\n", argv[0]);
        return EXIT_FAILURE;
    }

    if (strcmp(argv[1], "-Int64ToBytes") != 0) {
        fprintf(stderr, "Error: First argument must be '-Int64ToBytes'\n");
        return EXIT_FAILURE;
    }

    char *endptr;
    errno = 0;
    long long val = strtoll(argv[2], &endptr, 10);

    if (errno != 0 || *endptr != '\0') {
        fprintf(stderr, "Error: Invalid integer '%s'\n", argv[2]);
        return EXIT_FAILURE;
    }

    // 强制转换为 int64_t（确保在范围内）
    int64_t input = (int64_t)val;

    uint8_t bytes[8];
    int64_to_big_endian_bytes(input, bytes);

    // 打印为十六进制，每字节两位，无空格
    for (int i = 0; i < 8; ++i) {
        printf("%02X ", bytes[i]);
    }
    printf("\n");

    return EXIT_SUCCESS;
}