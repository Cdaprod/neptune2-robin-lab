# Raspberry Pi 5 network host

The Pi does not need to be physically next to the Neptune 2 when the printer's MKS ESP8266 is working on the same LAN.

## Current recovery state

The printer currently remembers the retired SSID `cda_FreshTomato24`, reports `IP: 0.0.0.0`, and its fallback `MKSWIFI7BED` AP is not usable from the phone. Therefore the host container cannot reach the printer yet.

Restore the ESP8266 to `cda_Lab` first. Keep the Robin printer firmware and ESP8266 firmware as separate concerns.

## Host layout

```text
Raspberry Pi 5
  └─ Docker
      └─ neptune2-robin-toolbox
          ├─ nmap
          ├─ curl
          ├─ netcat
          ├─ socat
          └─ neptune-robin Python CLI
                  │
                  │ cda_Lab / 192.168.0.0/24
                  ▼
            MKS ESP8266
                  │ UART
                  ▼
             Robin Nano v1.2
```

The container uses host networking so LAN discovery and direct access to MKS ports behave naturally on Linux/Raspberry Pi OS.

## Deploy

```bash
git clone https://github.com/Cdaprod/neptune2-robin-lab.git
cd neptune2-robin-lab
cp .env.example .env
chmod +x bin/neptune
make host-up
```

## Interactive shell

```bash
make host-shell
```

This gives an interactive shell containing the project CLI plus networking tools.

## Discovery after the ESP rejoins cda_Lab

```bash
make host-discover
```

The default scan range is `192.168.0.0/24`. Change `NEPTUNE_SUBNET` in `.env` if the LAN changes again.

Once a likely printer address appears:

```bash
make host-probe IP=192.168.0.123
```

The probe checks reachability, ports 80 and 8080, HTTP behavior, and sends a non-motion `M115` identity query to the MKS TCP endpoint.

After confirming the address, pin it in `.env`:

```dotenv
NEPTUNE_IP=192.168.0.123
```

Prefer assigning a DHCP reservation in the router/pfSense rather than configuring a static address directly on the ESP8266.

## Safety

The host tooling intentionally does not automatically home, heat, enable motors, or start a print. Discovery and read-only identity probes are acceptable automatic operations; machine actuation stays explicit.
