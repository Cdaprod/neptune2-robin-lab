# Recovery model

## 1. Host ↔ Robin USB

```bash
make doctor PORT=/dev/cu.usbserial-XXXX
```

Useful diagnostic G-code:

```text
M115 firmware identity
M105 temperatures
M21  init SD
M20  list SD
M114 position
M27  SD print status
```

## 2. Robin machine configuration

The factory-style Neptune 2 firmware consumes configuration from SD.

Recover a matching `elegoo.txt`, then patch only the Wi-Fi section.

## 3. MKS ESP8266

MKS documents these Robin-host signals:

```text
UART TX/RX
RESET
GPIO4 host-ready handshake
GPIO0 normal boot / flash mode
```

The Robin can update the module from:

```text
MksWifi.bin
```

placed on the printer SD card.

## 4. Desired LAN state

```text
mode: STA/client
SSID: cda_Lab
radio: 2.4 GHz
network: 192.168.0.0/24
address: DHCP
cloud: disabled
```

Once connected, use a DHCP reservation at the router/firewall for a stable
printer address rather than forcing a static address into every embedded
configuration.
