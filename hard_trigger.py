#!/usr/bin/env python3
"""Continuous GPIO pulse generation without a network server.

Sends an infinite pulse train on GPIO pins 20-27 simultaneously using the
modified WiringPi library. Useful for standalone triggering without TCP.

Usage:
    sudo python3 hard_trigger.py
    sudo python3 hard_trigger.py --num-pulses 100 --period-us 1500
    sudo python3 hard_trigger.py --mode motor
"""

import argparse
import signal
import sys
import time

import wiringpi

OUTPUT_PINS = [27, 22, 23, 24, 25]
INPUT_PINS = [26]
DEFAULT_PIN_MASK = 0xFF


def setup_gpio(pin_mask: int) -> None:
    wiringpi.wiringPiSetupGpio()
    for pin in OUTPUT_PINS:
        wiringpi.pinMode(pin, 1)
    for pin in INPUT_PINS:
        wiringpi.pinMode(pin, 0)
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))


def continuous_trigger(pin_mask: int, num_pulses: int, period_us: int) -> None:
    """Send pulse trains continuously in an infinite loop."""
    count = 0
    while True:
        wiringpi.sendPulseToRadar2(pin_mask, num_pulses, period_us, 1)
        count += 1
        if count % 100 == 0:
            print(f"Pulse trains sent: {count}")


def motor_trigger(pin_mask: int, num_pulses: int, period_us: int) -> None:
    """Wait for a rising edge on the input pin, then send a pulse train."""
    debounce_s = 0.001
    prev_t = time.time()
    count = 0

    while True:
        while wiringpi.digitalRead(26) == 0 or time.time() - prev_t < debounce_s:
            continue

        wiringpi.sendPulseToRadar2(pin_mask, num_pulses, period_us, 1)
        count += 1
        if count % 100 == 0:
            print(f"dt={time.time() - prev_t:.4f}s  count={count}")
        prev_t = time.time()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Continuous multi-pin GPIO pulse generation")
    parser.add_argument("--num-pulses", type=int, default=1,
                        help="Pulses per train (default: 1)")
    parser.add_argument("--period-us", type=int, default=1500,
                        help="Period between pulses in microseconds (default: 1500)")
    parser.add_argument("--pin-mask", type=lambda x: int(x, 0), default="0xff",
                        help="Bitmask for GPIO pins 20-27 (default: 0xff)")
    parser.add_argument("--mode", choices=["continuous", "motor"], default="continuous",
                        help="continuous: free-running loop; motor: trigger on input pin 26")
    args = parser.parse_args()

    setup_gpio(args.pin_mask)

    if args.mode == "motor":
        motor_trigger(args.pin_mask, args.num_pulses, args.period_us)
    else:
        continuous_trigger(args.pin_mask, args.num_pulses, args.period_us)


if __name__ == "__main__":
    main()
