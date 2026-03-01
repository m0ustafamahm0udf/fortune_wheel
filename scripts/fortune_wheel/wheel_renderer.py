"""
🎡 wheel_renderer.py — رسم العجلة
الـ class الرئيسي اللي بيرسم العجلة بكل تفاصيلها:
  - الشرائح الملونة مع الـ gradient
  - النصوص
  - حلقة التوهج (glow ring)
  - المؤشر (السهم الذهبي)
  - الدائرة المركزية (hub)
  - تأثير الفائز (pulse)
"""

import pygame
import math
from .colors import (
    WHEEL_COLORS, WHITE, ACCENT_GOLD, ACCENT_CYAN,
    CARD_DARK, SURFACE_DARK, PRIMARY,
    lerp_color, darken, brighten,
)
from .config import SEGMENT_COUNT


class FortuneWheel:
    def __init__(self, segment_count=SEGMENT_COUNT):
        self.segment_count = segment_count
        self.colors = [WHEEL_COLORS[i % len(WHEEL_COLORS)] for i in range(segment_count)]
        self.items = [f"No {i + 1}" for i in range(segment_count)]
        self.angle_rad = 0.0
        self.winner_index = -1
        self.pulse_phase = 0.0

        # Cache
        self._cached_wheel = None
        self._cached_size = 0

    # ── Public ──

    def set_angle_deg(self, deg):
        """تعيين زاوية الدوران بالدرجات."""
        self.angle_rad = math.radians(deg)

    def calculate_winner(self):
        """حساب الشريحة الفائزة (اللي تحت السهم)."""
        seg_angle = 2 * math.pi / self.segment_count
        norm = self.angle_rad % (2 * math.pi)
        adjusted = (2 * math.pi - norm) % (2 * math.pi)
        return round(adjusted / seg_angle) % self.segment_count

    def draw(self, screen, center, radius, dt):
        """رسم العجلة كاملة على الشاشة."""
        wheel_surf = self._build_wheel_surface(radius)

        self._draw_glow_ring(screen, center, radius)
        self._draw_rotated_wheel(screen, center, wheel_surf)
        self._draw_center_hub(screen, center, radius)
        self._draw_arrow(screen, center, radius)
        self._draw_winner_highlight(screen, center, radius, dt)

    # ── Private: بناء سطح العجلة (يتحدث مرة واحدة) ──

    def _build_wheel_surface(self, radius):
        size = int(radius * 2)
        if self._cached_wheel and self._cached_size == size:
            return self._cached_wheel

        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = radius, radius
        seg_angle = 2 * math.pi / self.segment_count

        for i in range(self.segment_count):
            self._draw_segment(surf, cx, cy, radius, i, seg_angle)

        # الإطار الخارجي
        pygame.draw.circle(surf, (*WHITE, 80), (int(cx), int(cy)), int(radius), 3)

        self._cached_wheel = surf
        self._cached_size = size
        return surf

    def _draw_segment(self, surf, cx, cy, radius, index, seg_angle):
        """رسم شريحة واحدة (اللون + الـ gradient + الخط الفاصل + النص)."""
        color = self.colors[index]
        dark_color = darken(color, 0.65)
        start_a = index * seg_angle - math.pi / 2 - seg_angle / 2
        steps = max(20, int(radius / 3))
        size = int(radius * 2)

        # ── اللون الأساسي ──
        points = [(cx, cy)]
        for s in range(steps + 1):
            a = start_a + seg_angle * s / steps
            points.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
        points.append((cx, cy))
        pygame.draw.polygon(surf, color, points)

        # ── Radial gradient overlay ──
        for g in range(5):
            t = g / 5.0
            r2 = radius * (1.0 - t * 0.4)
            c = lerp_color(dark_color, color, t)
            pts = [(cx, cy)]
            for s in range(steps + 1):
                a = start_a + seg_angle * s / steps
                pts.append((cx + r2 * math.cos(a), cy + r2 * math.sin(a)))
            pts.append((cx, cy))
            grad_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.polygon(grad_surf, (*c, 60), pts)
            surf.blit(grad_surf, (0, 0))

        # ── الخط الفاصل ──
        div_s = (cx + radius * 0.15 * math.cos(start_a), cy + radius * 0.15 * math.sin(start_a))
        div_e = (cx + radius * math.cos(start_a), cy + radius * math.sin(start_a))
        pygame.draw.line(surf, (*WHITE, 50), div_s, div_e, 2)

        # ── النص ──
        text_a = start_a + seg_angle / 2
        text_r = radius * 0.65
        tx = cx + text_r * math.cos(text_a)
        ty = cy + text_r * math.sin(text_a)

        font_size = max(14, int(radius / 12))
        font = pygame.font.SysFont("Arial", font_size, bold=True)
        label = font.render(self.items[index], True, WHITE)

        rot_deg = -math.degrees(text_a + math.pi / 2)
        rotated = pygame.transform.rotate(label, rot_deg)
        rect = rotated.get_rect(center=(tx, ty))
        surf.blit(rotated, rect)

    # ── Private: رسم المكونات الفرعية ──

    def _draw_glow_ring(self, screen, center, radius):
        """حلقة التوهج الذهبية حول العجلة."""
        glow_r = int(radius + 12)
        glow_surf = pygame.Surface((glow_r * 2 + 20, glow_r * 2 + 20), pygame.SRCALPHA)
        gc = glow_r + 10
        for i in range(15):
            alpha = max(0, 60 - i * 4)
            pygame.draw.circle(glow_surf, (*ACCENT_GOLD, alpha), (gc, gc), glow_r + i, 2)
        screen.blit(glow_surf, (center[0] - gc, center[1] - gc))

    def _draw_rotated_wheel(self, screen, center, wheel_surf):
        """رسم العجلة بعد تدويرها بالزاوية الحالية."""
        rot_deg = -math.degrees(self.angle_rad)
        rotated = pygame.transform.rotate(wheel_surf, rot_deg)
        rect = rotated.get_rect(center=center)
        screen.blit(rotated, rect)

    def _draw_center_hub(self, screen, center, radius):
        """الدائرة المركزية بالإطار الذهبي."""
        hub_r = int(radius * 0.18)

        # الظل
        pygame.draw.circle(screen, (0, 0, 0, 100), (center[0] + 2, center[1] + 3), hub_r + 2)
        # الجسم
        pygame.draw.circle(screen, CARD_DARK, center, hub_r)
        pygame.draw.circle(screen, SURFACE_DARK, center, hub_r - 4)
        # الإطار الذهبي
        pygame.draw.circle(screen, ACCENT_GOLD, center, hub_r, 3)
        # التوهج
        glow = pygame.Surface((hub_r * 4, hub_r * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*ACCENT_GOLD, 30), (hub_r * 2, hub_r * 2), hub_r + 6)
        screen.blit(glow, (center[0] - hub_r * 2, center[1] - hub_r * 2))

        # رمز الماسة (مرسوم)
        d = int(hub_r * 0.35)
        diamond_pts = [
            (center[0], center[1] - d),      # top
            (center[0] + d, center[1]),       # right
            (center[0], center[1] + d),       # bottom
            (center[0] - d, center[1]),       # left
        ]
        pygame.draw.polygon(screen, ACCENT_GOLD, diamond_pts)
        pygame.draw.polygon(screen, brighten(ACCENT_GOLD), diamond_pts, 2)

    def _draw_arrow(self, screen, center, radius):
        """السهم الذهبي (المؤشر) في الأعلى."""
        arrow_w, arrow_h = 26, 28
        top_y = center[1] - radius - 22

        tip = (center[0], top_y + arrow_h)
        tl = (center[0] - arrow_w // 2, top_y)
        tr = (center[0] + arrow_w // 2, top_y)
        pts = [tip, tl, tr]

        # الظل
        shadow_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        s_pts = [(p[0] + 1, p[1] + 3) for p in pts]
        pygame.draw.polygon(shadow_surf, (0, 0, 0, 80), s_pts)
        screen.blit(shadow_surf, (0, 0))

        # الجسم الذهبي
        pygame.draw.polygon(screen, ACCENT_GOLD, pts)

        # إضاءة خفيفة
        half_pts = [
            (center[0], top_y + arrow_h // 2),
            (center[0] - arrow_w // 4, top_y),
            (center[0] + arrow_w // 4, top_y),
        ]
        hl_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(hl_surf, (255, 255, 200, 60), half_pts)
        screen.blit(hl_surf, (0, 0))

        # الحدود البيضاء
        pygame.draw.polygon(screen, WHITE, pts, 2)

    def _draw_winner_highlight(self, screen, center, radius, dt):
        """تأثير النبض على الشريحة الفائزة."""
        if self.winner_index < 0:
            return

        self.pulse_phase += dt * 3.0
        pulse_alpha = int(100 + 80 * math.sin(self.pulse_phase))
        seg_angle = 2 * math.pi / self.segment_count
        win_start = (
            self.winner_index * seg_angle
            - math.pi / 2
            - seg_angle / 2
            + self.angle_rad
        )

        hc = int(radius + 10)
        hl_surf = pygame.Surface((hc * 2, hc * 2), pygame.SRCALPHA)
        pts = [(hc, hc)]
        steps = 30
        for s in range(steps + 1):
            a = win_start + seg_angle * s / steps
            pts.append((hc + radius * math.cos(a), hc + radius * math.sin(a)))
        pts.append((hc, hc))
        pygame.draw.polygon(hl_surf, (255, 255, 255, min(255, pulse_alpha)), pts)
        screen.blit(hl_surf, (center[0] - hc, center[1] - hc))
