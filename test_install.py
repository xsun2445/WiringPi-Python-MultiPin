#!/usr/bin/env python3
"""Installation verification test.

Tests both standard WiringPi functions and the custom multi-pin extensions.
Run with: sudo python3 test_install.py
"""

import sys

def test_import():
    print("1. Import wiringpi ... ", end="", flush=True)
    import wiringpi
    print("OK")
    return wiringpi

def test_setup(wp):
    print("2. wiringPiSetupGpio() ... ", end="", flush=True)
    result = wp.wiringPiSetupGpio()
    print(f"OK (returned {result})")

def test_standard_gpio(wp):
    """Test standard single-pin WiringPi functions."""
    pin = 27
    print(f"3. Standard GPIO (pin {pin}):", flush=True)

    print(f"   pinMode({pin}, OUTPUT) ... ", end="", flush=True)
    wp.pinMode(pin, 1)
    print("OK")

    print(f"   digitalWrite({pin}, HIGH) ... ", end="", flush=True)
    wp.digitalWrite(pin, 1)
    print("OK")

    print(f"   digitalRead({pin}) ... ", end="", flush=True)
    val = wp.digitalRead(pin)
    print(f"OK (value={val})")

    print(f"   digitalWrite({pin}, LOW) ... ", end="", flush=True)
    wp.digitalWrite(pin, 0)
    print("OK")

def test_byte_write(wp):
    """Test digitalWriteByte2 — writes to pins 20-27 simultaneously."""
    print("4. digitalWriteByte2 (pins 20-27):", flush=True)

    print("   digitalWriteByte2(0xff) ... ", end="", flush=True)
    wp.digitalWriteByte2(0xFF)
    print("OK (all HIGH)")

    print("   digitalWriteByte2(0x00) ... ", end="", flush=True)
    wp.digitalWriteByte2(0x00)
    print("OK (all LOW)")

def test_send_pulse(wp):
    """Test custom sendPulseToRadar function."""
    print("5. sendPulseToRadar(0xff, 5, 1000) ... ", end="", flush=True)
    wp.sendPulseToRadar(0xFF, 5, 1000)
    print("OK (5 pulses, 1000us period)")

def test_send_pulse2(wp):
    """Test custom sendPulseToRadar2 function."""
    print("6. sendPulseToRadar2(0xff, 5, 1000, 1) ... ", end="", flush=True)
    wp.sendPulseToRadar2(0xFF, 5, 1000, 1)
    print("OK (5 pulses, 1000us period, width=1)")

def main():
    print("=" * 50)
    print("WiringPi-Python-MultiPin Installation Test")
    print("=" * 50)
    print()

    try:
        wp = test_import()
        test_setup(wp)
        test_standard_gpio(wp)
        test_byte_write(wp)
        test_send_pulse(wp)
        test_send_pulse2(wp)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    print()
    print("All tests passed.")

if __name__ == "__main__":
    main()
