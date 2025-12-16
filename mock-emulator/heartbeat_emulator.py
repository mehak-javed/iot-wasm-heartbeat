#!/usr/bin/env python3
import socket
import time
import json
import random

def send_heartbeat():
    """Mock RISC-V MCU sending heartbeat"""
    device_id = 0x12345678
    uptime = 0
    
    while True:
        # Create heartbeat data
        heartbeat = {
            "device_id": device_id,
            "uptime": uptime,
            "status": 1,
            "temperature": 25.0 + random.uniform(-2, 2),
            "memory_used": 1024 + uptime % 100,
            "error_code": 0,
            "source": "mock-emulator"
        }
        
        # Send to server
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', 3456))
                s.sendall(json.dumps(heartbeat).encode('utf-8'))
                print(f"❤️  Sent heartbeat: uptime={uptime}s")
        except ConnectionRefusedError:
            print("❌ Server not running on port 3456")
            print("Start server first: python3 heartbeat_server.py")
        
        uptime += 5
        time.sleep(5)  # Send every 5 seconds

if __name__ == "__main__":
    print("🤖 Mock Heartbeat Emulator Started")
    print("📡 Connecting to localhost:3456")
    print("Press Ctrl+C to stop")
    send_heartbeat()