# Neptune 2 Robin Lab

Host-side toolkit for an **Elegoo Neptune 2** using a **ZNP/MKS Robin Nano v1.2**
(STM32F103VET6) with the optional **MKS Robin WiFi ESP8266** module.

```text
Mac/Linux host
   │
   ├── USB serial ───────────────► Robin Nano v1.2
   │                                  │
   │                                  ├── printer motion/heaters/SD
   │                                  └── UART/control ─► MKS WiFi ESP8266
   │
   └── LAN/Wi-Fi ──► ESP8266 ────────┘
                       ├── TCP 8080  raw printer control
                       ├── HTTP 80   MKS web/upload endpoint
                       └── UDP 8989  MKS discovery
```

The project keeps **USB**, **SD-card staging**, and **Wi-Fi** as distinct
transports. Robin Nano v1.2 USB is treated as printer serial/G-code, not as a
USB mass-storage view of the inserted SD card.

## Default machine profile

- Elegoo Neptune 2
- ZNP/MKS Robin Nano v1.2
- STM32F103VET6 @ 72 MHz
- firmware family: Elegoo/ZNP/MKS Robin
- USB: serial/G-code
- optional MKS Robin WiFi ESP8266
- ESP ↔ Robin: UART + RESET + GPIO4 ready + GPIO0 boot/flash
- MKS WiFi TCP control: `8080`
- MKS HTTP: `80`
- MKS discovery: UDP `8989`
- expected LAN: `192.168.0.0/24`
- default SSID: `cda_Lab`
- 2.4 GHz Wi-Fi
- MKS cloud disabled by default

See `config/machine.toml`.

## First run

```bash
make bootstrap
make ports
make doctor PORT=/dev/cu.usbserial-XXXX
```

## USB control

```bash
make doctor PORT=/dev/cu.usbserial-XXXX
make status PORT=/dev/cu.usbserial-XXXX
make send PORT=/dev/cu.usbserial-XXXX CMD='M115'
make console PORT=/dev/cu.usbserial-XXXX
```

`doctor` queries firmware identity, temperatures, and SD state.

## Wi-Fi configuration

Secrets are never committed:

```bash
cp .env.example .env
$EDITOR .env
```

```dotenv
WIFI_SSID=cda_Lab
WIFI_PASSWORD=change-me
MKS_WIFI_MODE=0
```

Put a known-good Neptune 2 / Robin Nano v1.2 configuration at:

```text
vendor/elegoo.txt
```

Then:

```bash
make wifi-config
```

The result is:

```text
build/elegoo.txt
```

The patcher changes only the Wi-Fi directives and preserves the rest of your
machine configuration.

If the original machine config is completely lost, recover the matching stock
Neptune 2 / v1.2 config first. Do not invent motion, thermistor, endstop, or
bed-level parameters merely to restore Wi-Fi.

`config/elegoo-wifi.fragment.txt` is therefore a **Wi-Fi fragment**, not a
complete machine configuration.

## Optional USB → printer-SD text write

Some Robin/Marlin builds support `M28`/`M29` SD writes over printer serial.

```bash
.venv/bin/neptune-robin   --port /dev/cu.usbserial-XXXX   sd-write-text build/elegoo.txt elegoo.txt
```

This is intentionally text-only. For firmware binaries, stage them on a
physically mounted SD card instead.

## Stage configuration to mounted SD

```bash
make sd-stage SD=/Volumes/NEPTUNE_SD
```

## Reflash/update MKS ESP8266 through the Robin board

Given a known-good upstream MKS image:

```bash
make wifi-firmware-stage   SD=/Volumes/NEPTUNE_SD   BIN=/path/to/MksWifi.bin
```

The Makefile copies it to the SD root as:

```text
MksWifi.bin
```

Safely eject, insert into the printer, and power-cycle.

## Discover the printer over Wi-Fi

```bash
make discover
```

Check a known DHCP address:

```bash
make wifi-doctor IP=192.168.0.123
```

This tests TCP 8080, HTTP 80, and attempts `M115` over TCP 8080.

## Make Wi-Fi look like a local serial port

For applications that insist on a serial device:

```bash
make bridge IP=192.168.0.123
```

This uses `socat` to create:

```text
/tmp/neptune2-mks
```

and bridges it to:

```text
192.168.0.123:8080
```

That provides a compatibility path for serial-oriented frontends while the
actual transport is Wi-Fi.

## Application boundary

Native/raw-network tools can use:

```text
<printer-ip>:8080
```

Useful integration classes:

- Pronterface/Printrun-style control
- Repetier-style control
- MKS-aware Cura integrations
- local API/front-end services
- monitoring/telemetry collectors
- automation workers
- serial-only tools through the PTY bridge

See `docs/APPS.md`.

## Security

Treat the ESP8266 as a trusted-LAN printer endpoint, not an Internet service.
Do not port-forward ports 80 or 8080. Use a VPN or authenticated gateway for
remote access.

## Commands

```bash
make
make bootstrap
make ports
make doctor PORT=/dev/cu.usbserial-XXXX
make status PORT=/dev/cu.usbserial-XXXX
make send PORT=/dev/cu.usbserial-XXXX CMD='M115'
make console PORT=/dev/cu.usbserial-XXXX

make wifi-config
make discover
make wifi-doctor IP=192.168.0.123
make bridge IP=192.168.0.123

make sd-stage SD=/Volumes/NEPTUNE_SD
make wifi-firmware-stage SD=/Volumes/NEPTUNE_SD BIN=/path/MksWifi.bin
make wifi-firmware-info

make test
```

## Upstream references

- https://github.com/makerbase-mks/MKS-WIFI
- https://github.com/makerbase-mks/MKS-Robin-Nano-V1.X
- https://github.com/makerbase-mks/Mks-Robin-Nano-Marlin2.0-Firmware
- https://github.com/NARUTOfzr/ZNP-Robin-Nano-V1.2-V1.3
- https://github.com/Klipper3d/klipper/blob/master/config/printer-elegoo-neptune2-2021.cfg

The current scope intentionally retains the Robin Nano + MKS WiFi architecture.
Klipper or alternate ESP firmware can be added later as separate profiles.
