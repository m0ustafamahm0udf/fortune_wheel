"""
buttons.py — أزرار التحكم على الشاشة
Flat design, no SRCALPHA surfaces. Direct draws only for RPi performance.
"""

import pygame
import math
from .colors import (
    WHITE, GREY_A8,
    PRIMARY, ERROR_RED, CARD_DARK,
    darken, brighten,
)


class Button:

    def __init__(self, x, y, w, h, text, color, icon=None, font_size=16):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.icon = icon
        self.font_size = font_size
        self.hovered = False
        self.pressed = False
        self.is_active = False
        self._font = None
        self._label = None

    def update_position(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.pressed = False
                return True
            self.pressed = False
        return False

    def draw(self, screen, dt):
        x, y, w, h = self.rect.x, self.rect.y, self.rect.w, self.rect.h

        if self.is_active:
            bg = PRIMARY
            border_color = WHITE
        elif self.pressed:
            bg = darken(self.color, 0.5)
        elif self.hovered:
            bg = brighten(self.color, 1.15)
        else:
            bg = self.color

        pygame.draw.rect(screen, bg, (x, y, w, h), border_radius=8)

        if not self.is_active:
            border_color = WHITE if self.hovered else GREY_A8
        pygame.draw.rect(screen, border_color, (x, y, w, h), 1, border_radius=8)

        if self._font is None:
            self._font = pygame.font.SysFont("Arial", self.font_size, bold=True)
            self._label = self._font.render(self.text, True, WHITE)
        label = self._label
        cx_btn, cy_btn = x + w // 2, y + h // 2

        if self.icon == 'play':
            tri_size = 10
            offset_x = -(label.get_width() // 2 + tri_size + 4)
            tri_cx = cx_btn + offset_x
            pts = [
                (tri_cx - 4, cy_btn - tri_size // 2),
                (tri_cx - 4, cy_btn + tri_size // 2),
                (tri_cx + tri_size // 2 - 2, cy_btn),
            ]
            pygame.draw.polygon(screen, WHITE, pts)
            screen.blit(label, label.get_rect(midleft=(tri_cx + tri_size // 2 + 2, cy_btn)))
        elif self.icon == 'stop':
            sq = 9
            offset_x = -(label.get_width() // 2 + sq + 4)
            sq_cx = cx_btn + offset_x
            pygame.draw.rect(screen, WHITE, (sq_cx - sq // 2, cy_btn - sq // 2, sq, sq))
            screen.blit(label, label.get_rect(midleft=(sq_cx + sq // 2 + 4, cy_btn)))
        elif self.icon == 'reset':
            r = 7
            offset_x = -(label.get_width() // 2 + r * 2 + 2)
            arc_cx = cx_btn + offset_x + r
            pygame.draw.arc(screen, WHITE,
                            (arc_cx - r, cy_btn - r, r * 2, r * 2),
                            0.3, 5.5, 2)
            ax = arc_cx + int(r * math.cos(0.3))
            ay = cy_btn - int(r * math.sin(0.3))
            pygame.draw.polygon(screen, WHITE, [
                (ax + 4, ay - 2), (ax - 2, ay - 5), (ax - 1, ay + 3)
            ])
            screen.blit(label, label.get_rect(midleft=(arc_cx + r + 4, cy_btn)))
        else:
            screen.blit(label, label.get_rect(center=(cx_btn, cy_btn)))


class ControlPanel:

    def __init__(self):
        self.btn_start = Button(0, 0, 130, 50, "START", (40, 180, 80), icon='play')
        self.btn_stop = Button(0, 0, 130, 50, "STOP", ERROR_RED, icon='stop')
        self.btn_reset = Button(0, 0, 130, 50, "RESET", PRIMARY, icon='reset')

        self.btn_fullscreen = Button(0, 0, 50, 40, "[ ]", CARD_DARK, font_size=14)
        self.btn_quit = Button(0, 0, 50, 40, "X", (100, 30, 30), font_size=18)

        self.all_buttons = [
            self.btn_start, self.btn_stop, self.btn_reset,
            self.btn_fullscreen, self.btn_quit,
        ]

    def layout(self, screen_w, screen_h):
        panel_w = 130 * 3 + 20 * 2
        start_x = (screen_w - panel_w) // 2
        btn_y = screen_h - 80

        self.btn_start.update_position(start_x, btn_y)
        self.btn_stop.update_position(start_x + 150, btn_y)
        self.btn_reset.update_position(start_x + 300, btn_y)

        self.btn_fullscreen.update_position(screen_w - 115, 12)
        self.btn_quit.update_position(screen_w - 58, 12)

    def handle_event(self, event):
        if self.btn_start.handle_event(event): return 'START'
        if self.btn_stop.handle_event(event): return 'STOP'
        if self.btn_reset.handle_event(event): return 'RESET'
        if self.btn_fullscreen.handle_event(event): return 'FULLSCREEN'
        if self.btn_quit.handle_event(event): return 'QUIT'
        return None

    def draw(self, screen, dt):
        for btn in self.all_buttons:
            btn.draw(screen, dt)
