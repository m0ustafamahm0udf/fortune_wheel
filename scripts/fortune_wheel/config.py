"""
⚙️ config.py — الإعدادات والثوابت
كل القيم اللي بتتحكم في شكل وسلوك العجلة.
"""

# ─── Serial (USB) ───
# IKS9 ESP32 board — على ماك بيظهر غالباً كـ /dev/cu.usbserial-* أو /dev/cu.SLAB_USBtoUART
SERIAL_PORT = '/dev/cu.usbserial-0001'
BAUD_RATE = 115200

# ─── Display ───
FPS = 60
WINDOW_W = 1024
WINDOW_H = 768

# ─── Wheel ───
SEGMENT_COUNT = 8

# ─── Smooth Rotation (RPi performance) ───
ROTATION_CACHE_STEPS = 720
STOP_LERP_SPEED = 8            # used only when velocity≈0 to settle on final angle
SYNC_CORRECTION_FACTOR = 0.1   # gentle nudge toward sensor's reported angle while spinning

# ─── IKS9 Encoder ───
# لفة كاملة = 3600 نبضة (من iks9/include/configure.h: AUTO_RESET_PULSES)
IKS9_PULSES_PER_REV = 3600
IKS9_DEG_PER_PULSE = 360.0 / IKS9_PULSES_PER_REV    # 0.1° per pulse
VELOCITY_EMA_ALPHA = 0.35       # تنعيم سرعة الزاوية المحسوبة محلياً
VELOCITY_STALE_MS = 500         # لو مفيش بيانات جديدة → اعتبر السرعة صفر
