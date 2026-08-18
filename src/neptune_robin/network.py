from __future__ import annotations

import socket
import time

TCP_PORT = 8080
HTTP_PORT = 80
UDP_DISCOVERY_PORT = 8989


def tcp_open(host: str, port: int, timeout: float = 1.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def tcp_command(host: str, command: str, port: int = TCP_PORT, timeout: float = 2.0) -> str:
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(0.5)
        sock.sendall((command.strip() + "\n").encode())
        chunks: list[bytes] = []
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                data = sock.recv(4096)
            except socket.timeout:
                break
            if not data:
                break
            chunks.append(data)
            if b"\nok" in b"".join(chunks).lower():
                break
        return b"".join(chunks).decode(errors="replace")


def discover(timeout: float = 2.0) -> list[tuple[str, str]]:
    found: dict[str, str] = {}
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(0.25)
        sock.bind(("", 0))
        sock.sendto(b"mkswifi\n", ("255.255.255.255", UDP_DISCOVERY_PORT))

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                data, addr = sock.recvfrom(512)
            except socket.timeout:
                continue
            text = data.decode(errors="replace").strip()
            if text.lower().startswith("mkswifi:"):
                found[addr[0]] = text
    return sorted(found.items())
