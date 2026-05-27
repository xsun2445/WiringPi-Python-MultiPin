#!/usr/bin/env python3
"""Quick smoke test for the sendPulseToRadar function."""

import wiringpi

wiringpi.wiringPiSetupGpio()
wiringpi.sendPulseToRadar(0xFF, 2, 1000)
print("Pulse sent successfully.")
