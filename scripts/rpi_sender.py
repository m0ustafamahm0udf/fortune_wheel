import asyncio
import websockets
import json
import threading
import socket
import sys

# Global state
CLIENTS = set()
server_loop = None
# sudo ufw allow 8080 IMPORTANT
async def register(websocket):
    CLIENTS.add(websocket)
    print(f"\n[SERVER] 📡 New connection from {websocket.remote_address}")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get("type") == "IDENTIFY":
                    platform = data.get("platform", "Unknown")
                    print(f"[SERVER] ✅ CONNECTION SUCCESS: App identified as [{platform}]")
                    await websocket.send(json.dumps({"command": "WELCOME", "message": "Connected to RPi Server"}))
            except Exception as e:
                pass # Ignore non-json or other messages
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if websocket in CLIENTS:
            CLIENTS.remove(websocket)
        print(f"[SERVER] ❌ App disconnected. (Connected apps: {len(CLIENTS)})")

async def _do_broadcast(payload):
    if not CLIENTS:
        print("\n⚠️  No apps connected! Command not sent.")
        return
    
    # Send to all connected clients
    for client in list(CLIENTS):
        try:
            await client.send(payload)
        except Exception:
            CLIENTS.remove(client)

def broadcast_command(command, params=None):
    if server_loop is None: return
    payload = json.dumps({"command": command, "params": params})
    # Schedule the broadcast in the server's event loop
    asyncio.run_coroutine_threadsafe(_do_broadcast(payload), server_loop)

async def server_main():
    global server_loop
    server_loop = asyncio.get_running_loop()
    
    # Detect Local IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()

    print(f"📡 RPi WebSocket Server active on port 8080")
    print(f"🔗 IP to enter in Web App: {local_ip}")
    print(f"🔗 Connection URL: ws://{local_ip}:8080/ws")
    
    async with websockets.serve(register, "0.0.0.0", 8080):
        await asyncio.Future()  # keep running

def run_server():
    asyncio.run(server_main())

def cli_interface():
    # Start server in a background thread
    threading.Thread(target=run_server, daemon=True).start()

    print("\n" + "="*40)
    print("🎡 Fortune Wheel SERVER Controller")
    print("="*40)
    
    while True:
        print("\nReady for command:")
        print("[1] SPIN")
        print("[2] RESET")
        print("[3] EXIT")
        choice = input("Select > ")

        if choice == "1":
            try:
                rps = float(input("Speed (rps, default 5.0) > ") or "5.0")
                dur = float(input("Duration (sec, default 4.0) > ") or "4.0")
                broadcast_command("SPIN", {"rps": rps, "duration": dur})
                print("✅ Broadcast SPIN sent.")
                
                if input("Reset now? (y/n) > ").lower() == 'y':
                    broadcast_command("RESET")
                    print("✅ Broadcast RESET sent.")
            except ValueError:
                print("❌ Error: Please enter valid numbers.")
        elif choice == "2":
            broadcast_command("RESET")
            print("✅ Broadcast RESET sent.")
        elif choice == "3":
            print("Shutting down...")
            break

if __name__ == "__main__":
    cli_interface()
