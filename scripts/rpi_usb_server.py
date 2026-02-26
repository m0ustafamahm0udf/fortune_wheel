import asyncio
import websockets
import json
import threading
import socket
import sys
import serial
import time

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

def serial_reader_task():
    """
    هذه الدالة تعمل في الخلفية:
    تتصل بمنفذ الـ USB، تقرأ القيم (الزوايا)، 
    وتقوم ببثها لتطبيق Flutter.
    """
    global ser_conn
    try:
        # إعداد الاتصال بالسيريال
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.05)
        ser.reset_input_buffer()
        ser_conn = ser # حفظ الاتصال في المتغير العالمي
        print(f"\n[USB] 🔌 Successfully connected to NodeMCU on {SERIAL_PORT}")
        
        while True:
            # إذا كان هناك بيانات قادمة عبر الـ USB
            if ser.in_waiting > 0:
                # قراءة كل البيانات المتاحة لتفريغ البافر وتجنب التراكم والتأخير
                lines = ser.read(ser.in_waiting).decode('utf-8', errors='ignore').split('\n')
                
                # أخذ آخر سطر مكتمل (السطر قبل الأخير لأنه قد يكون الأخير غير مكتمل بعد)
                # أو السطر الأخير إذا كان هناك سطر واحد فقط
                valid_line = None
                for line in reversed(lines):
                    line = line.strip()
                    if line:
                        valid_line = line
                        break
                        
                if not valid_line:
                    continue
                
                try:
                    # محاولة تحويل النص إلى رقم عشري (Float) يمثل الزاوية
                    angle = float(valid_line)
                    # إرسال الزاوية للتطبيق
                    broadcast_command("ANGLE", {"angle": angle})
                    # طباعة قيمة الزاوية على نفس السطر ليرى المستخدم أن البيانات تصل فعلاً
                    print(f"\r[USB] 🟢 Angle broadcasted: {angle}°    ", end="", flush=True)
                except ValueError:
                    # تفادي طباعة الأخطاء عن رسائل START/STOP/RESET
                    if valid_line.startswith("OK:"):
                        print(f"\n[USB] 🟢 NodeMCU Reply: {valid_line}")
                    else:
                        print(f"\n[USB] ⚠️ Invalid data: {valid_line}")
            else:
                 # راحة بسيطة للمعالج
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

if __name__ == "__main__":
    cli_interface()
