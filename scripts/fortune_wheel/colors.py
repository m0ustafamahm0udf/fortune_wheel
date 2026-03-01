"""
🎨 colors.py — الألوان
نفس ألوان التطبيق الأصلي (Flutter AppColors).
"""

# ─── Background & Surface ───
BG_COLOR     = (13, 13, 26)       # #0D0D1A  — الخلفية الرئيسية
CARD_DARK    = (26, 26, 46)       # #1A1A2E  — خلفية الكروت
SURFACE_DARK = (22, 33, 62)       # #16213E  — خلفية السطح

# ─── Brand Colors ───
PRIMARY      = (108, 99, 255)     # #6C63FF  — اللون الأساسي (بنفسجي)
ACCENT_GOLD  = (255, 215, 0)      # #FFD700  — ذهبي
ACCENT_CYAN  = (0, 245, 255)      # #00F5FF  — سيان

# ─── UI Colors ───
WHITE        = (255, 255, 255)
GREY_A8      = (168, 168, 168)
ERROR_RED    = (229, 57, 53)      # #E53935  — أحمر للخطأ

# ─── Wheel Segment Colors (نفس Flutter AppColors.wheelColors) ───
WHEEL_COLORS = [
    (255, 107, 107),   # Coral Red
    (78, 205, 196),    # Turquoise
    (255, 217, 61),    # Warm Yellow
    (108, 92, 231),    # Royal Purple
    (168, 230, 207),   # Soft Mint
    (255, 138, 101),   # Deep Peach
    (116, 185, 255),   # Soft Blue
    (162, 155, 254),   # Periwinkle
    (85, 230, 193),    # Bright Teal
    (255, 118, 117),   # Soft Salmon
    (253, 121, 168),   # Candy Pink
    (250, 177, 160),   # Light Orange
]


# ─── Helper Functions ───

def lerp_color(c1, c2, t):
    """خلط لونين بنسبة t (0 = c1, 1 = c2)."""
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )

def darken(color, factor=0.6):
    """تعتيم اللون."""
    return (int(color[0] * factor), int(color[1] * factor), int(color[2] * factor))

def brighten(color, factor=1.3):
    """تفتيح اللون."""
    return (
        min(255, int(color[0] * factor)),
        min(255, int(color[1] * factor)),
        min(255, int(color[2] * factor)),
    )
