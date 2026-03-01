"""
🔌 serial_manager.py — إدارة اتصال USB Serial مع NodeMCU
يشتغل في thread منفصل، يقرأ الزوايا، ويعيد الاتصال تلقائياً.
"""

import serial
import threading
import re
import time
from .config import SERIAL_PORT, BAUD_RATE

# ─── State ───
_ser_conn = None
_ser_lock = threading.Lock()
is_connected = False
current_angle_deg = 0.0
current_delay_ms = 0

_FRAME_PATTERN = re.compile(r'<([^>]+)>')


def send_command(cmd: str):
    """إرسال أمر للـ NodeMCU عبر USB.

    الأوامر المتاحة:
        START\\r\\n    — تشغيل المحرك
        STOP\\r\\n     — إيقاف المحرك
        RESET\\r\\n    — ريسيت
    """
    with _ser_lock:
        try:
            if _ser_conn and _ser_conn.is_open:
                _ser_conn.reset_output_buffer()
                _ser_conn.write(cmd.encode())
                _ser_conn.flush()
        except Exception as e:
            print(f"[USB] ❌ Send failed: {e}")


def _reader_loop():
    """الحلقة الأساسية لقراءة الزوايا — تعمل في thread خلفي."""
    global _ser_conn, is_connected, current_angle_deg, current_delay_ms

    while True:
        try:
            with _ser_lock:
                _ser_conn = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.05)
                _ser_conn.reset_input_buffer()
            is_connected = True
            print(f"[USB] 🔌 Connected to {SERIAL_PORT}")

            buf = ""
            while True:
                try:
                    with _ser_lock:
                        if _ser_conn is None or not _ser_conn.is_open:
                            break
                        waiting = _ser_conn.in_waiting

                    if waiting > 0:
                        with _ser_lock:
                            raw = _ser_conn.read(waiting).decode('utf-8', errors='ignore')
                        buf += raw

                        # طباعة ردود الـ NodeMCU
                        for ok_m in re.finditer(r'OK:[^\r\n]+', raw):
                            print(f"\n[USB] 🟢 {ok_m.group()}")

                        # استخراج الزوايا من الـ frames
                        frames = _FRAME_PATTERN.findall(buf)
                        last_gt = buf.rfind('>')
                        if last_gt != -1:
                            buf = buf[last_gt + 1:]

                        for fv in frames:
                            try:
                                parts = fv.split(',')
                                a = float(parts[0])
                                if 0.0 <= a < 360.0:
                                    current_angle_deg = a
                                if len(parts) >= 2:
                                    d = int(parts[1])
                                    if 1 <= d <= 5000:
                                        current_delay_ms = d
                                print(f"\r[USB] Angle: {a:.1f}° Delay: {current_delay_ms}ms    ", end="", flush=True)
                            except (ValueError, IndexError):
                                pass
                    else:
                        time.sleep(0.005)

                except OSError:
                    break

        except serial.SerialException as e:
            print(f"[USB] ❌ {e}")
        except Exception as e:
            print(f"[USB] ❌ Unknown: {e}")

        is_connected = False
        _ser_conn = None
        print("[USB] 🔄 Reconnecting in 3s...")
        time.sleep(3)


def start():
    """بدء thread قراءة الـ Serial في الخلفية."""
    t = threading.Thread(target=_reader_loop, daemon=True)
    t.start()
