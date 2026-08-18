# Application compatibility

## Native MKS network boundary

| Service | Port | Purpose |
|---|---:|---|
| HTTP | 80/tcp | MKS web/upload interface |
| Raw printer socket | 8080/tcp | G-code/control socket |
| Discovery | 8989/udp | MKS discovery |

For tools supporting a raw host/port:

```text
host: <printer DHCP address>
port: 8080
```

## Serial-only frontends

```bash
make bridge IP=192.168.0.123
```

Then use:

```text
/tmp/neptune2-mks
```

Architecture:

```text
frontend
  │ local PTY
  ▼
socat
  │ TCP/8080
  ▼
MKS WiFi ESP8266
  │ UART
  ▼
Robin Nano
```

## Custom/API frontends

Prefer a transport adapter boundary:

```text
HTTP / WebSocket / automation
            │
            ▼
      printer adapter
        │        │
        │        └── MKS TCP :8080
        └─────────── USB serial
                     │
                     ▼
                 Robin Nano
```

This allows professional/local applications to use the same logical printer
API regardless of whether the physical path is USB or Wi-Fi.
