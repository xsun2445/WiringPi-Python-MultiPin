# WiringPi-Python-MultiPin

Fork of [WiringPi-Python](https://github.com/WiringPi/WiringPi-Python) with support for **simultaneous multi-pin GPIO pulse generation** on Raspberry Pi.

Standard WiringPi can only toggle one GPIO pin at a time from Python. This fork adds C-level functions that drive GPIO pins 20-27 simultaneously via direct register writes (`digitalWriteByte2`), achieving microsecond-precision synchronized pulses across up to 8 pins.

## What was modified

**WiringPi C library** ([fork](https://github.com/xsun2445/WiringPi)):
- Added `sendPulseToRadar(num_loop, pd)` in `wiringPi.c` - generates a pulse train on pins 20-27 with configurable count and period
- Added `sendPulseToRadar2(pins, num_loop, pd, w)` - extended version with pin mask and pulse width control

**WiringPi-Python bindings** ([fork](https://github.com/xsun2445/WiringPi-Python)):
- Added SWIG declarations in `bindings.i` to expose the new C functions to Python
- Version bumped to 3.60.1

## Prerequisites

- Raspberry Pi (tested on ARM64 / Pi 5)
- Python 3 with development headers
- SWIG (optional - pre-generated wrapper is included)
- Build tools (gcc, make)

```bash
sudo apt-get update
sudo apt-get install python3-dev python3-setuptools swig build-essential
```

## Installation

### 1. Clone the repository

```bash
git clone --recursive https://github.com/xsun2445/WiringPi-Python-MultiPin.git
cd WiringPi-Python-MultiPin
```

If you already cloned without `--recursive`:

```bash
git submodule update --init --recursive
```

### 2. Install the WiringPi C library (optional, for the `gpio` CLI tool)

```bash
cd WiringPi-Python/WiringPi
./build debian
sudo dpkg -i debian-template/wiringpi_3.6_arm64.deb
cd ../..
```

### 3. Build and install the Python module

```bash
cd WiringPi-Python
sudo python3 setup.py install
cd ..
```

### 4. Verify

```python
import wiringpi
wiringpi.wiringPiSetupGpio()
wiringpi.sendPulseToRadar(0xff, 10, 1500)
```

## Usage

### Direct Python API

```python
import wiringpi

wiringpi.wiringPiSetupGpio()

# Send 100 pulses with 1500us period on all 8 pins (20-27)
wiringpi.sendPulseToRadar2(0xff, 100, 1500, 1)
```

### TCP trigger server

A TCP server that accepts trigger commands over the network:

```bash
sudo python3 trigger_server.py --port 5000
```

A client connects to a remote server and triggers on command:

```bash
sudo python3 trigger_client.py 192.168.1.100 --port 5000
```

See `--help` on either script for all options.

### Message protocol

Commands use the format: `{greeting}{delimiter}{num_frames}{delimiter}{period_ms}`

Default delimiter is `@$@$`. Example:

```
hello from server!@$@$100@$@$1500
```

## API Reference

| Function | Description |
|----------|-------------|
| `sendPulseToRadar(pins, num_loop, pd)` | Send `num_loop` pulses with `pd` microsecond period on GPIO pins selected by bitmask `pins` |
| `sendPulseToRadar2(pins, num_loop, pd, w)` | Same as above with pulse width `w` control |

## Troubleshooting

- **Permission errors** - GPIO access requires root. Run with `sudo`.
- **SWIG not found** - The build falls back to the pre-generated `wiringpi_wrap.c`. Install SWIG only if you modify the C code.
- **Import errors** - Make sure you installed with the same Python version you are running.
- **Empty submodule directories** - Run `git submodule update --init --recursive`.

## License

WiringPi is licensed under the GNU Lesser General Public License v3.0. See [LICENSE](WiringPi-Python/LICENSE.txt) for details.
