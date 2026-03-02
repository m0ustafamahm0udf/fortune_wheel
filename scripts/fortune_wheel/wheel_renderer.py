"""
wheel_renderer.py — رسم العجلة (lightweight)
تصميم بسيط بدون أي alpha blending في الـ render loop.
كل الرسم flat + direct draws على الشاشة.

Velocity-based local animation + pre-rendered rotation cache for smooth RPi performance.
"""

import pygame
import math
from .colors import WHEEL_COLORS, WHITE, ACCENT_GOLD, CARD_DARK, SURFACE_DARK, darken
from .config import SEGMENT_COUNT, ROTATION_CACHE_STEPS, STOP_LERP_SPEED, SYNC_CORRECTION_FACTOR


class FortuneWheel:
    def __init__(self, segment_count=SEGMENT_COUNT):
        self.segment_count = segment_count
        self.colors = [WHEEL_COLORS[i % len(WHEEL_COLORS)] for i in range(segment_count)]
        self.items = [f"No {i + 1}" for i in range(segment_count)]
        self.angle_rad = 0.0
        self._target_angle_rad = 0.0
        self._velocity_dps = 0.0
        self.winner_index = -1

        self._rot_cache = []
        self._rot_cache_size = 0
        self._rot_steps = ROTATION_CACHE_STEPS

        self._cached_wheel = None
        self._cached_size = 0

    def set_angle_deg(self, deg):
        """Set the reference angle from NodeMCU (cumulative degrees, can exceed 360)."""
        self._target_angle_rad = math.radians(deg)

    def set_velocity(self, dps):
        """Set angular velocity in degrees per second (from NodeMCU)."""
        self._velocity_dps = dps

    def update(self, dt):
        """Velocity-based local animation with gentle sync correction."""
        if self._velocity_dps > 0.0:
            self.angle_rad += math.radians(self._velocity_dps) * dt

            sync_diff = self._target_angle_rad - self.angle_rad
            self.angle_rad += sync_diff * SYNC_CORRECTION_FACTOR
        else:
            diff = self._target_angle_rad - self.angle_rad
            diff = (diff + math.pi) % (2 * math.pi) - math.pi

            if abs(diff) < 0.001:
                self.angle_rad = self._target_angle_rad
            else:
                self.angle_rad += diff * min(1.0, dt * STOP_LERP_SPEED)

    def calculate_winner(self):
        seg_angle = 2 * math.pi / self.segment_count
        norm = self.angle_rad % (2 * math.pi)
        adjusted = (2 * math.pi - norm) % (2 * math.pi)
        return round(adjusted / seg_angle) % self.segment_count

    def draw(self, screen, center, radius, dt):
        wheel_surf = self._build_wheel_surface(radius)
        self._ensure_rotation_cache(wheel_surf, radius)

        self._draw_rotated_wheel(screen, center)
        self._draw_center_hub(screen, center, radius)
        self._draw_arrow(screen, center, radius)

    # ── Build base wheel (once, cached) ──

    def _build_wheel_surface(self, radius):
        size = int(radius * 2)
        if self._cached_wheel and self._cached_size == size:
            return self._cached_wheel

        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = radius, radius
        seg_angle = 2 * math.pi / self.segment_count

        for i in range(self.segment_count):
            self._draw_segment(surf, cx, cy, radius, i, seg_angle)

        self._cached_wheel = surf
        self._cached_size = size
        self._rot_cache = []
        self._rot_cache_size = 0
        return surf

    def _draw_segment(self, surf, cx, cy, radius, index, seg_angle):
        color = self.colors[index]
        start_a = index * seg_angle - math.pi / 2 - seg_angle / 2
        steps = max(20, int(radius / 3))

        points = [(cx, cy)]
        for s in range(steps + 1):
            a = start_a + seg_angle * s / steps
            points.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
        points.append((cx, cy))
        pygame.draw.polygon(surf, color, points)

        text_a = start_a + seg_angle / 2
        text_r = radius * 0.55
        tx = cx + text_r * math.cos(text_a)
        ty = cy + text_r * math.sin(text_a)

        font_size = max(16, int(radius / 10))
        font = pygame.font.SysFont("Arial", font_size, bold=True)
        label = font.render(str(index + 1), True, WHITE)
        rect = label.get_rect(center=(tx, ty))
        surf.blit(label, rect)

    # ── Rotation cache ──

    def _ensure_rotation_cache(self, wheel_surf, radius):
        size = int(radius * 2)
        if self._rot_cache and self._rot_cache_size == size:
            return

        steps = self._rot_steps
        cache = [None] * steps
        for i in range(steps):
            deg = -i * (360.0 / steps)
            cache[i] = pygame.transform.rotate(wheel_surf, deg)
        self._rot_cache = cache
        self._rot_cache_size = size

    # ── Per-frame draws (no SRCALPHA, no surface allocation) ──

    def _draw_rotated_wheel(self, screen, center):
        if not self._rot_cache:
            return
        steps = self._rot_steps
        angle_deg = math.degrees(self.angle_rad) % 360.0
        idx = int(round(angle_deg * steps / 360.0)) % steps
        rotated = self._rot_cache[idx]
        rect = rotated.get_rect(center=center)
        screen.blit(rotated, rect)

    def _draw_center_hub(self, screen, center, radius):
        hub_r = int(radius * 0.18)
        pygame.draw.circle(screen, CARD_DARK, center, hub_r)
        pygame.draw.circle(screen, SURFACE_DARK, center, hub_r - 4)
        pygame.draw.circle(screen, ACCENT_GOLD, center, hub_r, 3)

    def _draw_arrow(self, screen, center, radius):
        arrow_w, arrow_h = 26, 28
        top_y = center[1] - int(radius) - 22

        tip = (center[0], top_y + arrow_h)
        tl = (center[0] - arrow_w // 2, top_y)
        tr = (center[0] + arrow_w // 2, top_y)
        pts = [tip, tl, tr]

        pygame.draw.polygon(screen, ACCENT_GOLD, pts)
        pygame.draw.polygon(screen, WHITE, pts, 2)
