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

# ─── أوامر مؤجلة (lock-free) ───
_pending_cmd = None
_cmd_lock = threading.Lock()


def send_command(cmd: str):
    """إرسال أمر للـ NodeMCU — يتحط في queue والـ reader thread يبعته.

    كده الـ Main Thread ما بيعملش lock على الـ Serial أبداً.
    """
    global _pending_cmd
    with _cmd_lock:
        _pending_cmd = cmd


def _flush_pending_cmd(conn):
    """يبعت أي أمر معلق — يتنادى من الـ reader thread بس."""
    global _pending_cmd
    with _cmd_lock:
        cmd = _pending_cmd
        _pending_cmd = None
    if cmd and conn and conn.is_open:
        try:
            conn.reset_output_buffer()
            conn.write(cmd.encode())
            conn.flush()
        except Exception as e:
            print(f"[USB] ❌ Send failed: {e}")


def _reader_loop():
    """الحلقة الأساسية لقراءة الزوايا — تعمل في thread خلفي."""
    global _ser_conn, is_connected, current_angle_deg, current_delay_ms

    while True:
        try:
            conn = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.05)
            conn.reset_input_buffer()
            with _ser_lock:
                _ser_conn = conn
            is_connected = True
            print(f"[USB] 🔌 Connected to {SERIAL_PORT}")

            buf = ""
            while True:
                try:
                    # ── أرسل أي أمر معلق الأول ──
                    _flush_pending_cmd(conn)

                    # ── اقرأ البيانات بدون lock ──
                    waiting = conn.in_waiting

                    if waiting > 0:
                        raw = conn.read(waiting).decode('utf-8', errors='ignore')
                        buf += raw

                        # طباعة ردود الـ NodeMCU
                        for ok_m in re.finditer(r'OK:[^\r\n]+', raw):
                            print(f"\n[USB] 🟢 {ok_m.group()}")

                        # استخراج الزوايا من الـ frames
                        frames = _FRAME_PATTERN.findall(buf)
                        last_gt = buf.rfind('>')
                        if last_gt != -1:
                            buf = buf[last_gt + 1:]

                        # خد آخر frame بس — الباقي قديم
                        if frames:
                            fv = frames[-1]
                            try:
                                parts = fv.split(',')
                                a = float(parts[0])
                                if 0.0 <= a < 360.0:
                                    current_angle_deg = a
                                if len(parts) >= 2:
                                    d = float(parts[1])
                                    if 0.1 <= d <= 5000:
                                        current_delay_ms = d
                            except (ValueError, IndexError):
                                pass
                    else:
                        time.sleep(0.002)

                except OSError:
                    break

        except serial.SerialException as e:
            print(f"[USB] ❌ {e}")
        except Exception as e:
            print(f"[USB] ❌ Unknown: {e}")

        is_connected = False
        with _ser_lock:
            _ser_conn = None
        print("[USB] 🔄 Reconnecting in 3s...")
        time.sleep(3)


def start():
    """بدء thread قراءة الـ Serial في الخلفية."""
    t = threading.Thread(target=_reader_loop, daemon=True)
    t.start()
