"""
🔌 serial_manager.py — قراءة بيانات الـ IKS9 Encoder عبر USB Serial

الـ IKS9 (firmware في مجلد iks9/) عبارة عن سنسور قراءة فقط — مش بيستقبل أوامر.
بيطبع كل ~300ms سطر بالشكل ده:

    0.50<TAB><TAB>0.8°<TAB><TAB>FWD<TAB><TAB>100<TAB><TAB>OK

أعمدة: distance(mm) | degrees | direction(FWD/REV) | pulses | status

الـ module ده:
  - بيقرأ الـ Serial في thread خلفي
  - بيستخرج عدد النبضات (pulses) ويحوله لزاوية تراكمية بدقة 0.1°/نبضة
  - بيحسب السرعة محلياً (Δangle / Δt) مع EMA smoothing
  - بيتعامل مع الـ auto-reset في الـ firmware (عند 3600 نبضة) كحدث non-velocity
  - بيوفّر zero_position() لإعادة الصفر بدون لمس الجهاز
"""

import re
import threading
import time

import serial

from .config import (
    SERIAL_PORT,
    BAUD_RATE,
    IKS9_PULSES_PER_REV,
    IKS9_DEG_PER_PULSE,
    VELOCITY_EMA_ALPHA,
    VELOCITY_STALE_MS,
)

# ─── State (مقروء من الـ GUI thread) ───
is_connected = False
current_angle_deg = 0.0          # cumulative degrees minus zero offset
current_velocity_dps = 0.0       # |dθ/dt| — موجبة دايماً (مناسبة للـ renderer)
current_distance_mm = 0.0        # كما يقرأها الـ firmware
current_pulses = 0               # raw pulses من آخر سطر
current_direction_fwd = True     # True = FWD
last_status = ""                 # OK | NEAR RESET | RESET EVENT

# ─── Internal ───
_lock = threading.Lock()
_cumulative_pulses = 0           # عدد النبضات التراكمي (بيتجاهل الـ resets)
_zero_pulses = 0                 # offset للـ RESET المحلي
_last_pulses_seen = None         # آخر raw pulses شفناه — لحساب الفرق
_last_sample_ts = 0.0            # ms — لحساب dt
_last_data_ts = 0.0              # ms — لاكتشاف انقطاع البيانات

# regex: float \s+ float° \s+ FWD/REV \s+ int \s+ status
_LINE_PATTERN = re.compile(
    r'^\s*(-?\d+\.?\d*)\s+(-?\d+\.?\d*)°\s+(FWD|REV)\s+(-?\d+)\s+(.+?)\s*$'
)


def _now_ms() -> float:
    return time.monotonic() * 1000.0


def _process_line(line: str) -> None:
    """يحلل سطر بيانات IKS9 ويحدّث الـ state. الأسطر الغير معروفة بتتجاهل بهدوء."""
    global current_angle_deg, current_velocity_dps
    global current_distance_mm, current_pulses, current_direction_fwd
    global last_status, _cumulative_pulses, _last_pulses_seen
    global _last_sample_ts, _last_data_ts

    line = line.strip()
    if not line:
        return

    # أحداث الـ firmware الخاصة
    if "Z PULSE RESET" in line or "AUTO-RESET" in line:
        with _lock:
            last_status = "RESET EVENT"
            # السطر ده بييجي مع/بعد قفزة في pulses → نمسح baseline عشان الـ delta التالي
            # ميتحسبش كحركة ضخمة
            _last_pulses_seen = None
        return

    m = _LINE_PATTERN.match(line)
    if not m:
        return  # header lines, banners, …

    try:
        distance_mm = float(m.group(1))
        # m.group(2) هي الدرجات المنرملة 0-360 من الـ firmware — مش هنعتمد عليها
        # علشان pulses يدّينا cumulative بدون wrap
        direction_fwd = (m.group(3) == "FWD")
        raw_pulses = int(m.group(4))
        status = m.group(5).strip()
    except (ValueError, IndexError):
        return

    now = _now_ms()

    with _lock:
        # ─── حساب الـ delta في pulses مع التعامل مع الـ auto-reset ───
        if _last_pulses_seen is None:
            delta = 0
        else:
            delta = raw_pulses - _last_pulses_seen
            # الـ firmware بيعمل reset عند ±3600 → نتجاهل أي قفزة أكبر من نصف لفة
            if abs(delta) > IKS9_PULSES_PER_REV // 2:
                delta = 0

        _cumulative_pulses += delta
        _last_pulses_seen = raw_pulses

        # ─── حساب الزاوية والسرعة ───
        new_angle_deg = (_cumulative_pulses - _zero_pulses) * IKS9_DEG_PER_PULSE

        if _last_sample_ts > 0 and delta != 0:
            dt_s = (now - _last_sample_ts) / 1000.0
            if dt_s > 0:
                instant_dps = abs(delta * IKS9_DEG_PER_PULSE) / dt_s
                current_velocity_dps = (
                    VELOCITY_EMA_ALPHA * instant_dps
                    + (1.0 - VELOCITY_EMA_ALPHA) * current_velocity_dps
                )
        elif delta == 0:
            # نبضات ثابتة → خفّض السرعة تدريجياً
            current_velocity_dps *= (1.0 - VELOCITY_EMA_ALPHA)
            if current_velocity_dps < 0.5:
                current_velocity_dps = 0.0

        current_angle_deg = new_angle_deg
        current_distance_mm = distance_mm
        current_pulses = raw_pulses
        current_direction_fwd = direction_fwd
        last_status = status
        _last_sample_ts = now
        _last_data_ts = now


def _watchdog_tick() -> None:
    """لو مفيش بيانات لفترة → السرعة = 0."""
    global current_velocity_dps
    with _lock:
        if _last_data_ts and (_now_ms() - _last_data_ts) > VELOCITY_STALE_MS:
            current_velocity_dps = 0.0


def zero_position() -> None:
    """RESET محلي — يخلي الزاوية الحالية = 0 بدون أي تواصل مع الجهاز."""
    global current_angle_deg, current_velocity_dps, _zero_pulses
    with _lock:
        _zero_pulses = _cumulative_pulses
        current_angle_deg = 0.0
        current_velocity_dps = 0.0
    print("[IKS9] 🔄 Zero offset applied")


def _reader_loop() -> None:
    """thread الـ background — readline-based لأن الـ firmware بيبعت سطور كاملة."""
    global is_connected, _last_pulses_seen

    while True:
        try:
            conn = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.2)
            conn.reset_input_buffer()
            is_connected = True
            print(f"[IKS9] 🔌 Connected to {SERIAL_PORT}")

            with _lock:
                _last_pulses_seen = None  # baseline جديد كل ما نتصل

            while True:
                try:
                    raw = conn.readline()
                except OSError:
                    break

                if raw:
                    try:
                        _process_line(raw.decode("utf-8", errors="ignore"))
                    except Exception as e:
                        print(f"[IKS9] ⚠ parse error: {e}")
                else:
                    _watchdog_tick()

        except serial.SerialException as e:
            print(f"[IKS9] ❌ {e}")
        except Exception as e:
            print(f"[IKS9] ❌ Unknown: {e}")

        is_connected = False
        print("[IKS9] 🔄 Reconnecting in 3s...")
        time.sleep(3)


def start() -> None:
    """ابدأ thread القراءة في الخلفية."""
    t = threading.Thread(target=_reader_loop, daemon=True)
    t.start()
