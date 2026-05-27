#!/usr/bin/env python3
"""TCP client that connects to a remote server and triggers GPIO pulses on command.

Runs on a Raspberry Pi. Connects to a host server, waits for trigger commands,
fires simultaneous multi-pin GPIO pulses, then sends an acknowledgment.

Protocol: the server sends a UTF-8 message in the format:
    {greeting}{delimiter}{num_frames}{delimiter}{period_ms}

The client replies with b"Done." after each trigger.
"""

import argparse
import socket
import time

import wiringpi

OUTPUT_PINS = [27, 22, 23, 24, 25]
INPUT_PINS = [26]
DEFAULT_PIN_MASK = 0xFF
DELIMITER = "@$@$"


class Trigger:
    """Controls simultaneous GPIO pulse generation via WiringPi."""

    def __init__(self, pin_mask: int = DEFAULT_PIN_MASK) -> None:
        wiringpi.wiringPiSetupGpio()
        for pin in OUTPUT_PINS:
            wiringpi.pinMode(pin, 1)
        for pin in INPUT_PINS:
            wiringpi.pinMode(pin, 0)
        self.pin_mask = pin_mask

    def send_pulse(self, num_pulses: int, period_us: int) -> None:
        wiringpi.sendPulseToRadar2(self.pin_mask, num_pulses, period_us, 1)


def connect_with_retry(host: str, port: int, retry_interval: float = 1.0) -> socket.socket:
    """Keep trying to connect until the server is available."""
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            return sock
        except OSError as e:
            print(f"Waiting for server {host}:{port} ... {e}")
            time.sleep(retry_interval)


def listen_and_trigger(host: str, port: int, trigger: Trigger) -> None:
    """Main loop: connect to server, receive commands, fire pulses."""
    sock = connect_with_retry(host, port)

    greeting = sock.recv(1024).decode()
    print(greeting.split(DELIMITER)[0])
    sock.send(b"Done.")

    count = 0
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                raise ConnectionError("Connection lost")
        except (ConnectionError, OSError) as e:
            print(f"Connection error: {e}. Reconnecting...")
            try:
                sock.close()
            except OSError:
                pass
            sock = connect_with_retry(host, port)
            sock.send(b"Done.")
            continue

        parts = data.split(DELIMITER)
        if len(parts) >= 3 and "hello from server!" in parts[0]:
            num_frames = int(parts[1])
            period_ms = float(parts[2])
            count += 1
            print(f"Trigger {count}: frames={num_frames}, period={period_ms}ms")
            trigger.send_pulse(num_frames, int(period_ms * 1e3))
            sock.send(b"Done.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TCP trigger client for simultaneous multi-pin GPIO pulses")
    parser.add_argument("host", help="Server IP address to connect to")
    parser.add_argument("--port", type=int, default=5000,
                        help="Server TCP port (default: 5000)")
    parser.add_argument("--pin-mask", type=lambda x: int(x, 0), default="0xff",
                        help="Bitmask for GPIO pins 20-27 (default: 0xff)")
    args = parser.parse_args()

    trigger = Trigger(pin_mask=args.pin_mask)
    listen_and_trigger(args.host, args.port, trigger)


if __name__ == "__main__":
    main()
