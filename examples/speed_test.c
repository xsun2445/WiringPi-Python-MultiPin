/*
 * speed_test.c - GPIO simultaneous write speed benchmark
 *
 * Measures how fast digitalWriteByte2() can toggle GPIO pins 20-27.
 * Requires the WiringPi library to be installed system-wide.
 *
 * Build:  gcc -O3 -o speed_test speed_test.c -lwiringPi -lpthread
 * Run:    sudo ./speed_test
 */

#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define ITERATIONS 10000000
#define PASSES     5

static void benchmark(int iterations)
{
    int i, pass;
    unsigned int start, end, total = 0;

    for (pass = 0; pass < PASSES; ++pass) {
        start = millis();
        for (i = 0; i < iterations; ++i)
            digitalWriteByte2(0xFF);
        end = millis();

        unsigned int elapsed = end - start;
        printf("  Pass %d: %u ms\n", pass + 1, elapsed);
        total += elapsed;
    }

    unsigned int avg = total / PASSES;
    int per_sec = (int)((double)iterations / ((double)avg / 1000.0));
    printf("  Average: %u ms  (%d writes/sec)\n", avg, per_sec);
}

static void pulse_loop(int pin_mask, int pulse_width_us, int period_us)
{
    printf("Continuous pulse loop (Ctrl-C to stop)...\n");
    for (;;) {
        digitalWriteByte2(pin_mask);
        delayMicroseconds(pulse_width_us);
        digitalWriteByte2(0x00);
        delayMicroseconds(period_us);
    }
}

int main(int argc, char *argv[])
{
    printf("WiringPi GPIO simultaneous write speed test\n");
    printf("============================================\n\n");

    wiringPiSetupGpio();
    for (int i = 1; i <= 8; i++)
        pinMode(i, OUTPUT);

    if (argc > 1 && argv[1][0] == 'p') {
        pulse_loop(0xFF, 2, 10);
    } else {
        printf("Benchmark: %d iterations x %d passes\n", ITERATIONS, PASSES);
        benchmark(ITERATIONS);
    }

    return 0;
}
