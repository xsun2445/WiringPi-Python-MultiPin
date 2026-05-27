CC      ?= gcc
CFLAGS   = -O3 -Wall
LDLIBS   = -lwiringPi -lpthread

.PHONY: all clean

all: examples/speed_test

examples/speed_test: examples/speed_test.c
	$(CC) $(CFLAGS) -o $@ $< $(LDLIBS)

clean:
	rm -f examples/speed_test
