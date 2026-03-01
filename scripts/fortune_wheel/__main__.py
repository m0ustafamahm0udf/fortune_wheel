"""نقطة الدخول لتشغيل الباكيج كـ module: python -m fortune_wheel أو python fortune_wheel"""
from fortune_wheel.config import *
from fortune_wheel.colors import *
from fortune_wheel.wheel_renderer import FortuneWheel
from fortune_wheel.buttons import ControlPanel
from fortune_wheel import serial_manager
from fortune_wheel import hud

# Re-use main() from the entry point
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fortune_wheel_gui import main

main()
