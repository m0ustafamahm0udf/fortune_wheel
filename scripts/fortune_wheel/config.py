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
ROTATION_CACHE_STEPS = 360
LERP_SPEED = 25
