"""
📊 hud.py — واجهة المعلومات (Heads-Up Display)
يعرض حالة الاتصال، الزاوية، والفائز.
"""

import pygame
import math
from .colors import WHITE, GREY_A8, ACCENT_GOLD, ACCENT_CYAN, ERROR_RED, PRIMARY
from .config import SERIAL_PORT


def draw(screen, wheel, connected, delay_ms):
    """رسم الـ HUD على الشاشة."""
    w, h = screen.get_size()

    font_title = pygame.font.SysFont("Arial", 28, bold=True)
    font_info = pygame.font.SysFont("Arial", 18)

    # ── العنوان ──
    title = font_title.render("Fortune Wheel", True, WHITE)
    screen.blit(title, (20, 15))

    # ── حالة الاتصال ──
    if connected:
        status_color = (80, 220, 100)
        status_text = f"Connected ({SERIAL_PORT})"
    else:
        status_color = ERROR_RED
        status_text = f"Disconnected ({SERIAL_PORT})"
    screen.blit(font_info.render(status_text, True, status_color), (20, 52))

    # ── الزاوية الحالية ──
    angle_deg = math.degrees(wheel.angle_rad) % 360
    screen.blit(font_info.render(f"Angle: {angle_deg:.1f}°", True, GREY_A8), (20, 78))

    # ── الديلاي الحالي + وقت اللفة الكاملة ──
    if delay_ms > 0:
        rotation_sec = 360 * delay_ms / 1000.0
        delay_text = f"Delay: {delay_ms}ms"
        rotation_text = f"Full rotation: {rotation_sec:.1f}s"
    else:
        delay_text = "Delay: --"
        rotation_text = "Full rotation: --"
    screen.blit(font_info.render(delay_text, True, ACCENT_CYAN), (20, 104))
    screen.blit(font_info.render(rotation_text, True, GREY_A8), (20, 130))

    # ── الفائز ──
    if wheel.winner_index >= 0:
        winner_label = font_title.render(
            f"Winner: {wheel.items[wheel.winner_index]}",
            True, ACCENT_GOLD,
        )
        screen.blit(winner_label, winner_label.get_rect(center=(w // 2, h - 140)))
