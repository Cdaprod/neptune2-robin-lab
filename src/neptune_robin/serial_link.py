from __future__ import annotations

import time
from pathlib import Path
import serial
from serial.tools import list_ports


def ports() -> list[dict[str, str]]:
    return [
        {"device": p.device, "description": p.description or "", "hwid": p.hwid or ""}
        for p in list_ports.comports()
    ]


class PrinterSerial:
    def __init__(self, port: str, baud: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.ser: serial.Serial | None = None

    def __enter__(self):
        self.ser = serial.Serial(self.port, self.baud, timeout=self.timeout)
        time.sleep(1.2)
        self.ser.reset_input_buffer()
        return self

    def __exit__(self, *exc):
        if self.ser:
            self.ser.close()

    def command(self, command: str, settle: float = 0.25, max_wait: float = 2.0) -> str:
        assert self.ser is not None
        self.ser.write((command.strip() + "\n").encode())
        self.ser.flush()
        deadline = time.monotonic() + max_wait
        chunks: list[str] = []
        last_data = time.monotonic()

        while time.monotonic() < deadline:
            raw = self.ser.readline()
            if raw:
                line = raw.decode(errors="replace").rstrip()
                chunks.append(line)
                last_data = time.monotonic()
                if line.strip().lower() == "ok":
                    break
            elif chunks and time.monotonic() - last_data >= settle:
                break
        return "\n".join(chunks)

    def sd_write_text(self, local_path: str | Path, remote_name: str) -> str:
        assert self.ser is not None
        text = Path(local_path).read_text(encoding="utf-8", errors="strict")
        begin = self.command(f"M28 {remote_name}", max_wait=3.0)
        if "error" in begin.lower():
            raise RuntimeError(begin)

        for line in text.splitlines():
            self.ser.write((line + "\n").encode())
            self.ser.flush()
            time.sleep(0.01)

        self.ser.write(b"M29\n")
        self.ser.flush()
        time.sleep(0.5)
        return self.command("M20", max_wait=3.0)
