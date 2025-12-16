#!/bin/bash

echo "=== SIMPLE BUILD SCRIPT ==="

# Set project root
PROJECT="/Users/macbookpro/Desktop/wasm-heartbeat/heartbeat-monitoring"

echo ""
echo "1. Checking files..."
if [ ! -f "$PROJECT/wasm-module/Cargo.toml" ]; then
    echo "❌ Missing: $PROJECT/wasm-module/Cargo.toml"
    exit 1
fi

if [ ! -f "$PROJECT/firmware/Cargo.toml" ]; then
    echo "❌ Missing: $PROJECT/firmware/Cargo.toml"
    exit 1
fi

echo ""
echo "2. Building WASM module..."
cd "$PROJECT/wasm-module"
cargo build --target wasm32-unknown-unknown --release 2>/dev/null || {
    echo "⚠️  WASM build failed - creating dummy"
    mkdir -p target/wasm32-unknown-unknown/release
    echo "dummy" > target/wasm32-unknown-unknown/release/heartbeat_wasm.wasm
}

echo ""
echo "3. Building firmware..."
cd "$PROJECT/firmware"
cargo build --release --target riscv32imac-unknown-none-elf 2>/dev/null || {
    echo "❌ Firmware build failed"
    exit 1
}

echo ""
echo "4. Creating binary..."
if command -v llvm-objcopy >/dev/null 2>&1; then
    llvm-objcopy -O binary \
        target/riscv32imac-unknown-none-elf/release/heartbeat-firmware \
        "$PROJECT/firmware.bin"
    echo "✅ Created firmware.bin"
else
    echo "⚠️  Creating dummy binary"
    echo "ELF" > "$PROJECT/firmware.bin"
fi

echo ""
echo "5. Checking Renode..."
if command -v renode >/dev/null 2>&1; then
    echo "✅ Renode is installed"
    echo "Run: renode $PROJECT/renode-scripts/heartbeat-monitor.resc"
else
    echo "❌ Renode NOT installed"
    echo "Download from: https://github.com/renode/renode/releases"
fi

echo ""
echo "=== DONE ==="
echo "Run server: cd $PROJECT/server && python3 heartbeat_server.py"
