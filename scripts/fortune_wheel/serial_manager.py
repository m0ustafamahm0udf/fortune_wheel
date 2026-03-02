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
current_velocity_dps = 0.0  # degrees per second from NodeMCU
current_step_deg = 5.0
current_delay_ms = 500

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
    global _ser_conn, is_connected, current_angle_deg, current_velocity_dps
    global current_step_deg, current_delay_ms

    while True:
        try:
            conn = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.05)
            conn.reset_input_buffer()
            with _ser_lock:
                _ser_conn = conn
            is_connected = True
            print(f"[USB] 🔌 Connected to {SERIAL_PORT}")
            
            # Request current step and delay upon connection
            send_command("INFO\r\n")
            
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

                        # استخراج أكواد OK من الـ buffer لمنع تقطيع البيانات
                        while "OK:" in buf:
                            idx = buf.find("OK:")
                            end_idx = buf.find("\n", idx)
                            if end_idx == -1:
                                break # الأمر مكملش لسه، استنى اللفة الجاية
                                
                            msg = buf[idx:end_idx].strip()
                            buf = buf[:idx] + buf[end_idx+1:] # إزالة الأمر من الـ buffer
                            
                            print(f"\n[USB] 🟢 {msg}")
                            if msg.startswith("OK:STEP:"):
                                try:
                                    current_step_deg = float(msg.split(":")[2])
                                except (ValueError, IndexError):
                                    pass
                            elif msg.startswith("OK:DELAY:"):
                                try:
                                    current_delay_ms = int(msg.split(":")[2])
                                except (ValueError, IndexError):
                                    pass

                        # استخراج الزوايا من الـ frames
                        frames = _FRAME_PATTERN.findall(buf)
                        last_gt = buf.rfind('>')
                        if last_gt != -1:
                            buf = buf[last_gt + 1:]

                        if frames:
                            fv = frames[-1]
                            try:
                                parts = fv.split(',')
                                a = float(parts[0])
                                current_angle_deg = a
                                if len(parts) >= 2:
                                    current_velocity_dps = float(parts[1])
                            except (ValueError, IndexError):
                                pass
                    else:
                        time.sleep(0.001)

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
