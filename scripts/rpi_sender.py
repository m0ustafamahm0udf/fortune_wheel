import asyncio
import websockets
import json
import threading
import socket
import sys
import time

# Global state
CLIENTS = set()

server_loop = None
SIMULATION_RUNNING = False
SIMULATION_THREAD = None
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

def simulation_task(step, delay_ms):
    global SIMULATION_RUNNING
    current_angle = 0.0
    
    while SIMULATION_RUNNING:
        broadcast_command("ANGLE", {"angle": current_angle})
        current_angle += step
        current_angle %= 360.0 
        time.sleep(delay_ms / 1000.0)

def cli_interface():
    # Start server in a background thread
    threading.Thread(target=run_server, daemon=True).start()
    
    global SIMULATION_RUNNING, SIMULATION_THREAD

    print("\n" + "="*40)
    print("🎡 Fortune Wheel SERVER Controller")
    print("="*40)
    
    while True:
        print("\nReady for command:")
        print("[1] START INFINITE SIMULATION")
        print("[2] STOP SIMULATION")
        print("[3] RESET")
        print("[4] EXIT")
        choice = input("Select > ")

        if choice == "1":
            if SIMULATION_RUNNING:
                print("⚠️ Simulation is already running!")
                continue

            try:
                step_val = float(input("Step Angle (default 2) > ") or "2")
                delay_ms = float(input("Delay (ms, default 50) > ") or "50")

                print(f"🔄 Starting infinite simulation with step {step_val} every {delay_ms}ms")
                SIMULATION_RUNNING = True
                SIMULATION_THREAD = threading.Thread(target=simulation_task, args=(step_val, delay_ms), daemon=True)
                SIMULATION_THREAD.start()
                
            except ValueError:
                print("❌ Error: Please enter valid numbers.")
        
        elif choice == "2":
            if SIMULATION_RUNNING:
                SIMULATION_RUNNING = False
                print("waiting for simulation to stop...")
                if SIMULATION_THREAD:
                    SIMULATION_THREAD.join()
                    SIMULATION_THREAD = None
                print("✅ Simulation stopped.")
            else:
                print("⚠️ Simulation is not running.")

        elif choice == "3":
            broadcast_command("RESET")
            print("✅ Broadcast RESET sent.")
        elif choice == "4":
            print("Shutting down...")
            break

if __name__ == "__main__":
    cli_interface()
