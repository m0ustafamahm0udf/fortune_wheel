import asyncio
import websockets
import json
import threading
import socket
import sys
import serial
import time
import re

# متغيرات الاتصال بالسيريال (USB)
SERIAL_PORT = '/dev/cu.usbserial-0001' # استبدله بـ /dev/ttyUSB0 أو /dev/ttyACM0 في الراسبيري
BAUD_RATE = 115200

# Global state
CLIENTS = set()
server_loop = None
ser_conn = None # متغير لتخزين الاتصال التسلسلي (Serial) لاستخدامه في إرسال الأوامر

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
                    await websocket.send(json.dumps({"command": "WELCOME", "message": "Connected to RPi USB Server"}))
                elif data.get("type") == "START":
                    if ser_conn:
                        ser_conn.reset_input_buffer()
                        ser_conn.reset_output_buffer()
                        ser_conn.write(b"START\r\n")
                        print("[USB] ✅ Sent START to NodeMCU.")
                elif data.get("type") == "STOP":
                    if ser_conn:
                        ser_conn.reset_output_buffer()
                        ser_conn.write(b"STOP\r\n")
                        print("[USB] ✅ Sent STOP to NodeMCU.")
                elif data.get("type") == "RESET":
                    if ser_conn:
                        ser_conn.reset_input_buffer()
                        ser_conn.reset_output_buffer()
                        ser_conn.write(b"RESET\r\n")
                        print("[USB] ✅ Sent RESET to NodeMCU.")
                    broadcast_command("RESET")
            except Exception:
                pass 
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if websocket in CLIENTS:
            CLIENTS.remove(websocket)
        print(f"[SERVER] ❌ App disconnected. (Connected apps: {len(CLIENTS)})")

async def _do_broadcast(payload):
    if not CLIENTS:
        return # لعدم إزعاج المستخدم برسائل التحذير المتكررة في وضع الـ USB
    
    for client in list(CLIENTS):
        try:
            await client.send(payload)
        except Exception:
            CLIENTS.remove(client)

def broadcast_command(command, params=None):
    if server_loop is None: return
    payload = json.dumps({"command": command, "params": params})
    asyncio.run_coroutine_threadsafe(_do_broadcast(payload), server_loop)

FRAME_PATTERN = re.compile(r'<([^>]+)>')
MIN_BROADCAST_INTERVAL = 0.016  # 16ms = ~60 broadcasts/sec max

def serial_reader_task():
    """
    تتصل بمنفذ الـ USB، تقرأ القيم (الزوايا) باستخدام framing markers،
    وتقوم ببثها لتطبيق Flutter.
    تستخدم بافر تراكمي لتجنب قراءة أسطر مقطوعة.
    """
    global ser_conn
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.05)
        ser.reset_input_buffer()
        ser_conn = ser
        print(f"\n[USB] 🔌 Successfully connected to NodeMCU on {SERIAL_PORT}")
        
        serial_buffer = ""
        last_broadcast_time = 0.0
        
        while True:
            if ser.in_waiting > 0:
                raw = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                serial_buffer += raw
                
                for ok_match in re.finditer(r'OK:\w+', raw):
                    print(f"\n[USB] 🟢 NodeMCU Reply: {ok_match.group()}")
                
                frames = FRAME_PATTERN.findall(serial_buffer)
                
                last_complete = serial_buffer.rfind('>')
                if last_complete != -1:
                    serial_buffer = serial_buffer[last_complete + 1:]
                
                if not frames:
                    if len(serial_buffer) > 256:
                        serial_buffer = serial_buffer[-64:]
                    continue
                
                last_valid_angle = None
                for frame_val in frames:
                    try:
                        angle = float(frame_val)
                        if 0.0 <= angle < 360.0:
                            last_valid_angle = angle
                    except ValueError:
                        pass
                
                if last_valid_angle is not None:
                    now = time.monotonic()
                    if now - last_broadcast_time >= MIN_BROADCAST_INTERVAL:
                        last_broadcast_time = now
                        broadcast_command("ANGLE", {"angle": last_valid_angle})
                        print(f"\r[USB] Angle: {last_valid_angle}    ", end="", flush=True)
            else:
                time.sleep(0.01)

    except serial.SerialException as e:
        print(f"\n[USB] ❌ ERROR: Could not connect to {SERIAL_PORT}.")
        print(f"Details: {e}")
        print("💡 TIP: Verify the USB is plugged in, and SERIAL_PORT is correct (e.g., /dev/ttyUSB0).")
    except Exception as e:
        print(f"\n[USB] ❌ Unknown Error: {e}")

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

    print(f"📡 WebSocket Server active on port 8080")
    print(f"🔗 IP to enter in Web App: {local_ip}")
    
    async with websockets.serve(register, "0.0.0.0", 8080):
        await asyncio.Future()  # keep running

def run_server():
    asyncio.run(server_main())

def cli_interface():
    print("\n" + "="*45)
    print("🎡 Fortune Wheel USB-WebSocket SERVER")
    print("="*45)
    
    # Start WebSocket server in a background thread
    threading.Thread(target=run_server, daemon=True).start()
    
    # Start USB Serial Reader in a background thread
    threading.Thread(target=serial_reader_task, daemon=True).start()
    
    # واجهة التحكم مبسطة لأن المحاكاة تتم الآن عبر الـ NodeMCU
    while True:
        print("\nCommands:")
        print("[1] SEND RESET COMMAND")
        print("[2] EXIT SERVER")
        print("[3] START WHEEL (NodeMCU)")
        print("[4] STOP WHEEL (NodeMCU)")
        print("[5] SET SPEED (DELAY MS)")
        choice = input("Select > ")

        if choice == "1":
            if ser_conn:
                ser_conn.reset_input_buffer()
                ser_conn.reset_output_buffer()
                ser_conn.write(b"RESET\r\n")
            broadcast_command("RESET")
            print("✅ Broadcast RESET sent.")
        elif choice == "2":
            print("Shutting down...")
            break
        elif choice == "3":
            if ser_conn:
                ser_conn.reset_input_buffer()
                ser_conn.reset_output_buffer()
                ser_conn.write(b"START\r\n")
                print("✅ Sent START command to NodeMCU.")
            else:
                print("❌ USB Not connected yet.")
        elif choice == "4":
            if ser_conn:
                ser_conn.reset_output_buffer()
                ser_conn.write(b"STOP\r\n")
                print("✅ Sent STOP command to NodeMCU.")
            else:
                print("❌ USB Not connected yet.")
        elif choice == "5":
            if ser_conn:
                val = input("Enter delay in ms (1-5000, current default=50): ")
                try:
                    ms = int(val)
                    if 1 <= ms <= 5000:
                        ser_conn.write(f"SPEED:{ms}\r\n".encode())
                        print(f"✅ Sent SPEED:{ms} to NodeMCU.")
                    else:
                        print("❌ Value must be between 10 and 500.")
                except ValueError:
                    print("❌ Invalid number.")
            else:
                print("❌ USB Not connected yet.")

if __name__ == "__main__":
    cli_interface()
