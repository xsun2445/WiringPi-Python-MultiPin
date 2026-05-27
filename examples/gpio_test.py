#!/usr/bin/env python3
"""Continuous GPIO pulse generation using RPi.GPIO (no WiringPi).

Simple example that toggles multiple GPIO pins as fast as possible in a loop.
Useful for basic testing without the WiringPi library installed.
"""

import signal
import sys

import RPi.GPIO as GPIO

PINS = [18, 14, 15, 17]


def main() -> None:
    signal.signal(signal.SIGINT, lambda *_: (GPIO.cleanup(), sys.exit(0)))

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PINS, GPIO.OUT)
    GPIO.output(PINS, 0)

    try:
        while True:
            GPIO.output(PINS, 1)
            GPIO.output(PINS, 0)
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
