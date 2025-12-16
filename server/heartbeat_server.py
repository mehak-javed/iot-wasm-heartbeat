#!/usr/bin/env python3
import socket
import json
import time
from datetime import datetime
import threading
import cbor2
import signal
import sys

class HeartbeatServer:
    def __init__(self, host='localhost', port=3456):
        self.host = host
        self.port = port
        self.running = True
        self.devices = {}
        
    def start(self):
        """Start the TCP server to listen for heartbeat messages"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(1)
            print(f"✅ Heartbeat server listening on {self.host}:{self.port}")
            print(f"📡 Connect your Renode emulator to this port")
            
            # Handle graceful shutdown
            signal.signal(signal.SIGINT, self.signal_handler)
            
            while self.running:
                client_socket, client_address = server_socket.accept()
                print(f"🔗 Connected by {client_address}")
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except Exception as e:
            print(f"❌ Server error: {e}")
        finally:
            server_socket.close()
    
    def handle_client(self, client_socket, client_address):
        """Handle incoming heartbeat messages"""
        buffer = ""
        
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                # Decode and process messages
                message = data.decode('utf-8', errors='ignore').strip()
                
                if message:
                    # Try to parse as JSON
                    try:
                        heartbeat_data = json.loads(message)
                        self.process_heartbeat(heartbeat_data, client_address)
                    except json.JSONDecodeError:
                        # Try CBOR if JSON fails
                        try:
                            heartbeat_data = cbor2.loads(data)
                            self.process_heartbeat(heartbeat_data, client_address)
                        except:
                            print(f"📥 Raw message from {client_address}: {message}")
        
        except Exception as e:
            print(f"⚠️ Error handling client {client_address}: {e}")
        finally:
            client_socket.close()
            print(f"🔌 Disconnected {client_address}")
    
    def process_heartbeat(self, data, source):
        """Process and display heartbeat data"""
        device_id = data.get('device_id', 'unknown')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Update device status
        self.devices[device_id] = {
            'last_seen': timestamp,
            'uptime': data.get('uptime', 0),
            'status': data.get('status', 0),
            'temperature': data.get('temperature', 0.0),
            'memory_used': data.get('memory_used', 0),
            'error_code': data.get('error_code', 0),
            'source': source
        }
        
        # Display heartbeat
        print("\n" + "="*50)
        print(f"❤️  HEARTBEET RECEIVED")
        print("="*50)
        print(f"Device ID:   0x{device_id:08X}")
        print(f"Timestamp:   {timestamp}")
        print(f"Uptime:      {data.get('uptime', 0)} seconds")
        print(f"Status:      {'✅ OK' if data.get('status', 0) == 1 else '⚠️ ERROR'}")
        print(f"Temperature: {data.get('temperature', 0.0):.1f}°C")
        print(f"Memory Used: {data.get('memory_used', 0)} bytes")
        print(f"Error Code:  {data.get('error_code', 0)}")
        print("="*50)
        
        # Display device summary
        self.display_summary()
    
    def display_summary(self):
        """Display summary of all monitored devices"""
        print("\n📊 DEVICE SUMMARY:")
        print("-"*60)
        print(f"{'Device ID':<12} {'Last Seen':<20} {'Status':<10} {'Uptime':<10}")
        print("-"*60)
        
        for device_id, info in self.devices.items():
            status_emoji = "✅" if info['status'] == 1 else "⚠️"
            print(f"0x{device_id:08X}  {info['last_seen']:<20} {status_emoji:<10} {info['uptime']:<10}s")
        print("-"*60)
        print(f"Total devices: {len(self.devices)}")
    
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n👋 Shutting down heartbeat server...")
        self.running = False
        sys.exit(0)

if __name__ == "__main__":
    # Install required packages
    try:
        import pyserial
        import cbor2
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Start server
    server = HeartbeatServer()
    server.start()