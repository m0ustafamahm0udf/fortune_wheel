import asyncio
import websockets
import json
import struct
import threading
import socket
import sys
import serial
import time
import re

# متغيرات الاتصال بالسيريال (USB)
SERIAL_PORT = '/dev/ttyUSB0' # Ensure this is correct, not /dev/ttyUSB01
BAUD_RATE = 115200

# Global state
CLIENTS = set()
server_loop = None
ser_conn = None # متغير لتخزين الاتصال التسلسلي (Serial) لاستخدامه في إرسال الأوامر

def send_command(command_str):
    global ser_conn
    try:
        if ser_conn and ser_conn.is_open:
            ser_conn.reset_output_buffer()
            if isinstance(command_str, str):
                ser_conn.write(command_str.encode())
            else:
                ser_conn.write(command_str)
            ser_conn.flush()
        else:
            print("\n[USB] ❌ Cannot send command, serial port is not connected.")
    except (serial.SerialException, OSError) as e:
        print(f"\n[USB] ❌ Failed to send command (Port disconnected?): {e}")


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
                    send_command("START\r\n")
                    print("[USB] ✅ Sent START to NodeMCU.")
                elif data.get("type") == "STOP":
                    send_command("STOP\r\n")
                    print("[USB] ✅ Sent STOP to NodeMCU.")
                elif data.get("type") == "RESET":
                    send_command("RESET\r\n")
                    print("[USB] ✅ Sent RESET to NodeMCU.")
                    reset_angle_tracking()
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

_last_sent_angle = 0.0

def broadcast_angle(angle_float):
    """Send angle delta as 1-byte binary (int8 signed)."""
    global _last_sent_angle
    if server_loop is None: return

    delta = angle_float - _last_sent_angle
    if delta < -180: delta += 360.0
    if delta > 180: delta -= 360.0

    _last_sent_angle = angle_float

    delta_int = int(round(delta))
    if delta_int == 0: return

    delta_int = max(-128, min(127, delta_int))
    payload = struct.pack('>b', delta_int)
    asyncio.run_coroutine_threadsafe(_do_broadcast(payload), server_loop)

def reset_angle_tracking():
    global _last_sent_angle
    _last_sent_angle = 0.0

FRAME_PATTERN = re.compile(r'<([^>]+)>')
MIN_BROADCAST_INTERVAL = 0.016  # 16ms = ~60 broadcasts/sec max

def serial_reader_task():
    """
    تتصل بمنفذ الـ USB، تقرأ القيم (الزوايا) باستخدام framing markers،
    وتقوم ببثها لتطبيق Flutter.
    يقوم هذا التاسك أيضاً بإعادة الاتصال تلقائياً عند فقدان الاتصال.
    """
    global ser_conn
    while True:
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.05)
            ser.reset_input_buffer()
            ser_conn = ser
            print(f"\n[USB] 🔌 Successfully connected to NodeMCU on {SERIAL_PORT}")
            
            serial_buffer = ""
            last_broadcast_time = 0.0
            
            while True:
                try:
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
                                broadcast_angle(last_valid_angle)
                                print(f"\r[USB] Angle: {last_valid_angle}    ", end="", flush=True)
                    else:
                        time.sleep(0.01)
                except OSError as inner_e:
                    print(f"\n[USB] ❌ Connection error during read: {inner_e}")
                    ser_conn = None
                    break # Break inner loop to reconnect
                
        except serial.SerialException as e:
            print(f"\n[USB] ❌ ERROR: Could not connect to {SERIAL_PORT}.")
            print(f"Details: {e}")
        except Exception as e:
            print(f"\n[USB] ❌ Unknown Error: {e}")
            
        # الانتظار قبل محاولة إعادة الاتصال (Auto-Reconnect)
        print("[USB] 🔄 Retrying connection in 3 seconds...")
        time.sleep(3)

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
            send_command("RESET\r\n")
            reset_angle_tracking()
            broadcast_command("RESET")
            print("✅ Broadcast RESET sent.")
        elif choice == "2":
            print("Shutting down...")
            break
        elif choice == "3":
            send_command("START\r\n")
            print("✅ Sent START command to NodeMCU.")
        elif choice == "4":
            send_command("STOP\r\n")
            print("✅ Sent STOP command to NodeMCU.")
        elif choice == "5":
            val = input("Enter delay in ms (1-5000, current default=50): ")
            try:
                ms = int(val)
                if 1 <= ms <= 5000:
                    send_command(f"SPEED:{ms}\r\n")
                    print(f"✅ Sent SPEED:{ms} to NodeMCU.")
                else:
                    print("❌ Value must be between 10 and 5000.")
            except ValueError:
                print("❌ Invalid number.")

if __name__ == "__main__":
    cli_interface()
