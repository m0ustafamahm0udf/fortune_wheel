#!/usr/bin/env python3
"""
🎡 Fortune Wheel — Pygame GUI for Raspberry Pi
نقطة الدخول — يجمع كل الأجزاء ويشغل اللعبة.

التحكم عبر أزرار على الشاشة + كيبورد كاختصار:
  S / زر START   → تشغيل
  X / زر STOP    → إيقاف + تحديد الفائز
  R / زر RESET   → ريسيت
  F / زر ⛶       → Fullscreen
  Q / زر ✕       → خروج
"""

import pygame
import os
import sys

from fortune_wheel.config import FPS, WINDOW_W, WINDOW_H, SEGMENT_COUNT
from fortune_wheel.colors import BG_COLOR, PRIMARY
from fortune_wheel.wheel_renderer import FortuneWheel
from fortune_wheel.buttons import ControlPanel
from fortune_wheel import serial_manager
from fortune_wheel import hud


def _handle_command(command, wheel, is_fullscreen, screen, panel):
    """تنفيذ أمر — يرجع (is_fullscreen, screen, running)."""
    running = True

    if command == 'START':
        # IKS9 سنسور قراءة فقط — مفيش حاجة تتبعت. مجرد تجهيز اللعبة.
        wheel.winner_index = -1
        print("[CMD] ▶ START — clearing winner, awaiting rotation")

    elif command == 'STOP':
        # نقفل الفائز على الزاوية الحالية اللي قراها السنسور
        wheel.winner_index = wheel.calculate_winner()
        print(f"[CMD] ⏹ STOP → Winner: {wheel.items[wheel.winner_index]}")

    elif command == 'RESET':
        serial_manager.zero_position()
        wheel.winner_index = -1
        wheel.set_angle_deg(0)
        wheel.set_velocity(0)
        print("[CMD] 🔄 RESET")

    elif command == 'FULLSCREEN':
        is_fullscreen = not is_fullscreen
        if is_fullscreen:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.RESIZABLE)

    elif command == 'QUIT':
        running = False

    return is_fullscreen, screen, running


# ── ربط الكيبورد بالأوامر ──
KEY_MAP = {
    pygame.K_s: 'START',
    pygame.K_x: 'STOP',
    pygame.K_r: 'RESET',
    pygame.K_f: 'FULLSCREEN',
    pygame.K_q: 'QUIT',
    pygame.K_ESCAPE: 'QUIT',
}


def main():
    pygame.init()
    pygame.display.set_caption("🎡 Fortune Wheel — RPi")

    # ── إعداد الشاشة ──
    is_fullscreen = False
    if os.path.exists('/dev/cu.usbserial-0001'):
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        is_fullscreen = True
    else:
        screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.RESIZABLE)

    clock = pygame.time.Clock()
    wheel = FortuneWheel(SEGMENT_COUNT)
    panel = ControlPanel()

    # ── بدء قراءة الـ Serial ──
    serial_manager.start()

    running = True

    # ── الحلقة الرئيسية ──
    while running:
        dt = clock.tick(FPS) / 1000.0
        w, h = screen.get_size()

        # ── ترتيب مواقع الأزرار حسب حجم الشاشة ──
        panel.layout(w, h)

        # ── معالجة الأحداث ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            # أزرار الشاشة
            btn_command = panel.handle_event(event)
            if btn_command:
                is_fullscreen, screen, running = _handle_command(
                    btn_command, wheel, is_fullscreen, screen, panel
                )

            # اختصارات الكيبورد
            if event.type == pygame.KEYDOWN:
                key_command = KEY_MAP.get(event.key)
                if key_command:
                    is_fullscreen, screen, running = _handle_command(
                        key_command, wheel, is_fullscreen, screen, panel
                    )

        # ── تحديث الزاوية والسرعة من الـ Serial ──
        wheel.set_angle_deg(serial_manager.current_angle_deg)
        wheel.set_velocity(serial_manager.current_velocity_dps)
        wheel.update(dt)

        # ── الرسم ──
        screen.fill(BG_COLOR)

        # العجلة
        wheel_radius = min(w, h) * 0.33
        wheel_center = (w // 2, h // 2 - 20)
        wheel.draw(screen, wheel_center, wheel_radius, dt)

        # واجهة المعلومات
        hud.draw(screen, wheel, serial_manager.is_connected)

        # أزرار التحكم
        panel.draw(screen, dt)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
