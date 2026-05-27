#!/usr/bin/env python3
"""TCP server that listens for trigger commands and generates GPIO pulse trains.

Runs on a Raspberry Pi. Accepts connections on a configurable port and triggers
simultaneous multi-pin GPIO pulses via the modified WiringPi library.

Protocol: the client sends a UTF-8 message in the format:
    {greeting}{delimiter}{num_frames}{delimiter}{period_ms}

The server replies with b"Done." after triggering, then waits for the next
connection.
"""

import argparse
import socket
from typing import Callable

import wiringpi

OUTPUT_PINS = [27, 22, 23, 24, 25]
INPUT_PINS = [26]
DEFAULT_PIN_MASK = 0xFF


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
        """Send a pulse train on all masked GPIO pins simultaneously.

        Args:
            num_pulses: Number of pulses to generate.
            period_us:  Period between pulses in microseconds.
        """
        wiringpi.sendPulseToRadar2(self.pin_mask, num_pulses, period_us, 1)


def run_server(bind_ip: str,
               port: int,
               delimiter: str,
               greeting: str,
               on_trigger: Callable[[int, int], None]) -> None:
    """Accept TCP connections and dispatch trigger commands.

    Each connection is expected to send exactly one command, after which the
    server replies and closes the connection.
    """
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((bind_ip, port))
    srv.listen(1)
    print(f"Trigger server listening on {bind_ip}:{port}")

    while True:
        conn, addr = srv.accept()
        print(f"Client connected from {addr}", end="", flush=True)
        with conn:
            try:
                conn.settimeout(10)
                data = conn.recv(256)
                if not data:
                    print(" empty message; closing.")
                    continue

                text = data.decode(errors="ignore")
                parts = text.split(delimiter)

                if len(parts) >= 3 and parts[0] == greeting:
                    num_frames = int(parts[1])
                    period_ms = int(parts[2])
                    print(f"  frames={num_frames}, period={period_ms}ms ...", end="", flush=True)
                    conn.sendall(b"Done.")
                    on_trigger(num_frames, period_ms)
                    print(" done.")
                else:
                    conn.sendall(b"Bad command")
                    print(f" bad command: {text!r}")
            except ValueError:
                conn.sendall(b"Bad command")
            except Exception as e:
                print(f" error: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="TCP trigger server for simultaneous multi-pin GPIO pulses")
    parser.add_argument("--bind-ip", default="0.0.0.0",
                        help="IP address to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5000,
                        help="TCP port (default: 5000)")
    parser.add_argument("--delimiter", default="@$@$",
                        help="Message field delimiter (default: @$@$)")
    parser.add_argument("--greeting", default="hello from server!",
                        help="Expected greeting prefix in messages")
    parser.add_argument("--pin-mask", type=lambda x: int(x, 0), default="0xff",
                        help="Bitmask for GPIO pins 20-27 (default: 0xff)")
    args = parser.parse_args()

    trigger = Trigger(pin_mask=args.pin_mask)

    def on_trigger(num_frames: int, period_ms: int) -> None:
        trigger.send_pulse(num_frames, int(period_ms * 1e3))

    run_server(
        bind_ip=args.bind_ip,
        port=args.port,
        delimiter=args.delimiter,
        greeting=args.greeting,
        on_trigger=on_trigger,
    )


if __name__ == "__main__":
    main()
