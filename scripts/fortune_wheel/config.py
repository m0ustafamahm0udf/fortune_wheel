"""
⚙️ config.py — الإعدادات والثوابت
كل القيم اللي بتتحكم في شكل وسلوك العجلة.
"""

# ─── Serial (USB) ───
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
STOP_LERP_SPEED = 8            # used only when velocity=0 to settle on final angle
SYNC_CORRECTION_FACTOR = 0.1   # gentle nudge toward NodeMCU's reported angle while spinning
