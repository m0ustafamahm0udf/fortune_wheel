"""
hud.py — واجهة المعلومات (Heads-Up Display)
يعرض حالة الاتصال، الزاوية، والفائز.
"""

import pygame
import math
from .colors import WHITE, GREY_A8, ACCENT_GOLD, ACCENT_CYAN, ERROR_RED, PRIMARY
from .config import SERIAL_PORT

_font_title = None
_font_info = None


def _get_fonts():
    global _font_title, _font_info
    if _font_title is None:
        _font_title = pygame.font.SysFont("Arial", 28, bold=True)
        _font_info = pygame.font.SysFont("Arial", 18)
    return _font_title, _font_info


def draw(screen, wheel, connected):
    """رسم الـ HUD على الشاشة."""
    w, h = screen.get_size()

    font_title, font_info = _get_fonts()

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
    from . import serial_manager
    angle_deg = math.degrees(wheel.angle_rad) % 360
    screen.blit(font_info.render(f"Angle: {angle_deg:.1f}°", True, GREY_A8), (20, 78))

    # ── بيانات الـ IKS9 ──
    speed_text = f"Speed: {serial_manager.current_velocity_dps:.1f} °/s"
    dist_text = (
        f"Distance: {serial_manager.current_distance_mm:.1f} mm  |  "
        f"Pulses: {serial_manager.current_pulses}  |  "
        f"{'FWD' if serial_manager.current_direction_fwd else 'REV'}"
    )
    screen.blit(font_info.render(speed_text, True, ACCENT_CYAN), (20, 104))
    screen.blit(font_info.render(dist_text, True, GREY_A8), (20, 130))

    # ── الفائز ──
    if wheel.winner_index >= 0:
        winner_label = font_title.render(
            f"Winner: {wheel.items[wheel.winner_index]}",
            True, ACCENT_GOLD,
        )
        screen.blit(winner_label, winner_label.get_rect(center=(w // 2, h - 140)))
