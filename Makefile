SHELL := /bin/bash
.RECIPEPREFIX := >

PYTHON ?= python3
VENV ?= .venv
CLI := $(VENV)/bin/neptune-robin
PORT ?=
BAUD ?= 115200
CMD ?= M115
IP ?=
SD ?=
BIN ?=

.DEFAULT_GOAL := help

.PHONY: help bootstrap ports doctor status send console wifi-config discover wifi-doctor bridge sd-stage wifi-firmware-stage wifi-firmware-info host-up host-down host-shell host-status host-discover host-probe test clean

help:
> @echo "Neptune 2 Robin Lab"
> @echo
> @echo "Local USB / Python tooling:"
> @echo "  make bootstrap"
> @echo "  make ports"
> @echo "  make doctor PORT=/dev/cu.usbserial-XXXX"
> @echo "  make status PORT=/dev/cu.usbserial-XXXX"
> @echo "  make send PORT=/dev/cu.usbserial-XXXX CMD='M115'"
> @echo "  make console PORT=/dev/cu.usbserial-XXXX"
> @echo
> @echo "Printer Wi-Fi / SD tooling:"
> @echo "  make wifi-config"
> @echo "  make discover"
> @echo "  make wifi-doctor IP=192.168.0.123"
> @echo "  make bridge IP=192.168.0.123"
> @echo "  make sd-stage SD=/Volumes/NEPTUNE_SD"
> @echo "  make wifi-firmware-stage SD=/Volumes/NEPTUNE_SD BIN=/path/MksWifi.bin"
> @echo "  make wifi-firmware-info"
> @echo
> @echo "Raspberry Pi / Docker host:"
> @echo "  make host-up"
> @echo "  make host-status"
> @echo "  make host-discover"
> @echo "  make host-probe IP=192.168.0.123"
> @echo "  make host-shell"
> @echo "  make host-down"
> @echo
> @echo "  make test"

bootstrap:
> @test -d "$(VENV)" || $(PYTHON) -m venv "$(VENV)"
> $(VENV)/bin/python -m pip install -e .

ports: bootstrap
> $(CLI) ports

doctor: bootstrap
> @test -n "$(PORT)" || (echo "PORT is required"; exit 2)
> $(CLI) --port "$(PORT)" --baud "$(BAUD)" doctor

status: bootstrap
> @test -n "$(PORT)" || (echo "PORT is required"; exit 2)
> $(CLI) --port "$(PORT)" --baud "$(BAUD)" status

send: bootstrap
> @test -n "$(PORT)" || (echo "PORT is required"; exit 2)
> $(CLI) --port "$(PORT)" --baud "$(BAUD)" send "$(CMD)"

console: bootstrap
> @test -n "$(PORT)" || (echo "PORT is required"; exit 2)
> $(CLI) --port "$(PORT)" --baud "$(BAUD)" console

wifi-config: bootstrap
> @test -f vendor/elegoo.txt || (echo "Missing vendor/elegoo.txt: recover a correct Neptune 2 v1.2 config first"; exit 2)
> @mkdir -p build
> $(CLI) wifi-config vendor/elegoo.txt build/elegoo.txt --env .env

discover: bootstrap
> $(CLI) discover

wifi-doctor: bootstrap
> @test -n "$(IP)" || (echo "IP is required"; exit 2)
> $(CLI) wifi-doctor "$(IP)"

bridge:
> @test -n "$(IP)" || (echo "IP is required"; exit 2)
> ./scripts/mks-pty-bridge.sh "$(IP)"

sd-stage:
> @test -n "$(SD)" || (echo "SD is required"; exit 2)
> @test -f build/elegoo.txt || (echo "Run make wifi-config first"; exit 2)
> cp -v build/elegoo.txt "$(SD)/elegoo.txt"
> sync
> @echo "Staged. Safely eject the SD card before removing it."

wifi-firmware-stage:
> @test -n "$(SD)" || (echo "SD is required"; exit 2)
> @test -n "$(BIN)" || (echo "BIN is required"; exit 2)
> @test -f "$(BIN)" || (echo "BIN does not exist: $(BIN)"; exit 2)
> cp -v "$(BIN)" "$(SD)/MksWifi.bin"
> sync
> @echo "Staged as $(SD)/MksWifi.bin"
> @echo "Safely eject, insert into printer, then power-cycle."

wifi-firmware-info:
> @echo "Upstream: https://github.com/makerbase-mks/MKS-WIFI"
> @echo "Expected SD filename: MksWifi.bin"
> @echo "Target: Generic ESP8266 Module"
> @echo "Flash mode: DOUT"
> @echo "Flash size: 4M (3M SPIFFS)"
> @echo "Runtime ports: TCP 8080, HTTP 80, UDP 8989"

host-up:
> chmod +x bin/neptune
> ./bin/neptune up

host-down:
> ./bin/neptune down

host-shell:
> chmod +x bin/neptune
> ./bin/neptune shell

host-status:
> chmod +x bin/neptune
> ./bin/neptune status

host-discover:
> chmod +x bin/neptune
> ./bin/neptune discover

host-probe:
> chmod +x bin/neptune
> @test -n "$(IP)" || (echo "IP is required"; exit 2)
> ./bin/neptune probe "$(IP)"

test: bootstrap
> $(VENV)/bin/python -m unittest discover -s tests -v

clean:
> rm -rf build/*
> mkdir -p build
> touch build/.gitkeep
