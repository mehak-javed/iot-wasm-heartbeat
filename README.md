# WASM-Based Heartbeat Monitoring from an Emulated RISC-V MCU

## Overview
This project implements a simulated Industrial IoT heartbeat monitoring system using an emulated RISC-V microcontroller running inside Renode. The system demonstrates how WebAssembly (WASM) can be used to execute modular and updateable application logic on constrained embedded devices while enabling reliable edge-to-cloud communication.

A lightweight WebAssembly runtime is integrated into the firmware, allowing a WASM module to generate and transmit periodic heartbeat messages containing device telemetry to a host-based server.

---

## Objective
The objective of this project is to design and implement a secure, modular, and remotely updateable heartbeat monitoring mechanism for an embedded RISC-V device. The project focuses on:

- Executing WASM-based logic on an emulated MCU
- Periodic transmission of heartbeat telemetry
- Reliable communication between edge and server
- Demonstrating updateability by replacing WASM modules at runtime

---

## System Description

### Emulated Embedded Device
- A RISC-V microcontroller (e.g., GD32VF103) is emulated using Renode.
- The firmware integrates the Wasm3 WebAssembly runtime.
- The firmware loads and executes a WASM module that implements heartbeat logic.
- UART is used as the communication interface, mapped to a TCP socket in Renode.

### WASM Heartbeat Module
- The WASM module is responsible for generating heartbeat payloads.
- Each heartbeat contains:
  - Device ID
  - Uptime
  - Status code
  - Basic telemetry data
- The module is designed to be replaceable without rebuilding the entire firmware.

### Communication Protocol
- Heartbeat messages are transmitted from the MCU over UART.
- Renode redirects UART output to a TCP socket.
- Messages are encoded using JSON or CBOR.

### Server Application
- A Python-based TCP server receives heartbeat messages.
- The server decodes, logs, and displays incoming telemetry.
- Device status is tracked in real time.
- Multiple devices can be monitored concurrently.

---

## Technologies Used
- **Renode** – RISC-V MCU emulation
- **RISC-V Architecture** – Embedded target platform
- **WebAssembly (WASM)** – Modular application logic
- **Wasm3** – Lightweight WASM runtime for embedded systems
- **Rust & C** – Firmware and WASM module development
- **Python** – Server-side heartbeat receiver
- **UART / Virtual Networking** – Communication interface
- **JSON / CBOR** – Heartbeat message encoding

---

## Build and Run Instructions

### 1. Build the WASM Module
```bash
cd wasm-module
cargo build --target wasm32-unknown-unknown --release

### 2.  Build Firmware
cd firmware
cargo build --release --target riscv32imac-unknown-none-elf

Generate Firmware Binary
llvm-objcopy -O binary target/riscv32imac-unknown-none-elf/release/heartbeat-firmware firmware.bin
4. Run the Server
cd server
python3 heartbeat_server.py


Terminal 1 - Start Server:(inside the server)

cd server
source venv/bin/activate
python3 heartbeat_server.py



Terminal 2 - Run Mock Emulator: (inside mock-emulator)


cd mock-emulator
python3 heartbeat_emulator.py
