#include "stdint.h"
#include <stdio.h>
#include <string.h>

float a = 105415610.123456789f;

int main(void) {
    uint8_t bytes[4];
    memcpy(bytes, &a, 4);
    for (int i=0; i<4; i++) {
        printf("%02X ", bytes[3-i]);
    }
    printf("\n");
    return 0;
}
