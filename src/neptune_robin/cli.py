from __future__ import annotations

import argparse
import json
import sys

from .serial_link import PrinterSerial, ports
from .network import discover, tcp_open, tcp_command, TCP_PORT, HTTP_PORT
from .wifi_config import patch_file


def require_port(args):
    if not args.port:
        raise SystemExit("--port is required for this command")


def cmd_ports(_args):
    ps = ports()
    if not ps:
        print("No serial ports found.")
        return
    for p in ps:
        print(f"{p['device']}\t{p['description']}\t{p['hwid']}")


def cmd_doctor(args):
    require_port(args)
    with PrinterSerial(args.port, args.baud) as printer:
        for command in ("M115", "M105", "M21", "M20"):
            print(f"\n>>> {command}")
            print(printer.command(command, max_wait=3.0) or "(no response)")


def cmd_status(args):
    require_port(args)
    with PrinterSerial(args.port, args.baud) as printer:
        for command in ("M105", "M114", "M27"):
            print(f"\n>>> {command}")
            print(printer.command(command, max_wait=2.0) or "(no response)")


def cmd_send(args):
    require_port(args)
    with PrinterSerial(args.port, args.baud) as printer:
        print(printer.command(args.command, max_wait=args.wait))


def cmd_console(args):
    require_port(args)
    print("Interactive G-code console. Ctrl-D or 'quit' exits.")
    with PrinterSerial(args.port, args.baud) as printer:
        while True:
            try:
                command = input("neptune> ").strip()
            except EOFError:
                print()
                break
            if not command:
                continue
            if command.lower() in {"q", "quit", "exit"}:
                break
            print(printer.command(command, max_wait=3.0))


def cmd_sd_write_text(args):
    require_port(args)
    with PrinterSerial(args.port, args.baud) as printer:
        print(printer.sd_write_text(args.local_path, args.remote_name))


def cmd_wifi_config(args):
    print(patch_file(args.source, args.output, args.env))


def cmd_discover(args):
    found = discover(args.timeout)
    if not found:
        print("No MKS WiFi modules replied on UDP 8989.")
        return 1
    for ip, reply in found:
        print(f"{ip}\t{reply}")
    return 0


def cmd_wifi_doctor(args):
    result = {
        "ip": args.ip,
        "tcp_8080": tcp_open(args.ip, TCP_PORT),
        "http_80": tcp_open(args.ip, HTTP_PORT),
    }
    if result["tcp_8080"]:
        try:
            result["m115"] = tcp_command(args.ip, "M115").strip()
        except OSError as exc:
            result["m115_error"] = str(exc)
    print(json.dumps(result, indent=2))
    return 0 if result["tcp_8080"] else 1


def build_parser():
    parser = argparse.ArgumentParser(prog="neptune-robin")
    parser.add_argument("--port")
    parser.add_argument("--baud", type=int, default=115200)
    sub = parser.add_subparsers(dest="subcommand", required=True)

    p = sub.add_parser("ports"); p.set_defaults(func=cmd_ports)
    p = sub.add_parser("doctor"); p.set_defaults(func=cmd_doctor)
    p = sub.add_parser("status"); p.set_defaults(func=cmd_status)

    p = sub.add_parser("send")
    p.add_argument("command")
    p.add_argument("--wait", type=float, default=2.0)
    p.set_defaults(func=cmd_send)

    p = sub.add_parser("console"); p.set_defaults(func=cmd_console)

    p = sub.add_parser("sd-write-text")
    p.add_argument("local_path")
    p.add_argument("remote_name")
    p.set_defaults(func=cmd_sd_write_text)

    p = sub.add_parser("wifi-config")
    p.add_argument("source")
    p.add_argument("output")
    p.add_argument("--env", default=".env")
    p.set_defaults(func=cmd_wifi_config)

    p = sub.add_parser("discover")
    p.add_argument("--timeout", type=float, default=2.0)
    p.set_defaults(func=cmd_discover)

    p = sub.add_parser("wifi-doctor")
    p.add_argument("ip")
    p.set_defaults(func=cmd_wifi_doctor)
    return parser


def main():
    args = build_parser().parse_args()
    try:
        rc = args.func(args)
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0 if rc is None else rc


if __name__ == "__main__":
    raise SystemExit(main())
