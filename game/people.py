from pathlib import Path
import math

import pygame


PORTRAIT_DIR = Path(__file__).resolve().parents[1] / "assets" / "portraits"
_PORTRAIT_CACHE = {}


def _load_portrait(role):
    role = {
        "customer": "support.jpeg",
        "docs": "integration",
        "support": "support.png",
        "accounting": "buh",
        "legacy": "legacy",
        "manager": "manager",
    }.get(role, role)
    if role not in _PORTRAIT_CACHE:
        path = PORTRAIT_DIR / role
        if not path.suffix:
            path = PORTRAIT_DIR / f"{role}.png"
        if path.exists():
            _PORTRAIT_CACHE[role] = pygame.image.load(str(path)).convert()
        else:
            _PORTRAIT_CACHE[role] = None
    return _PORTRAIT_CACHE[role]


def draw_avatar(surface, rect, role, colors, selected=False):
    """Рисует переданный портрет с аккуратным кадрированием."""
    rect = pygame.Rect(rect)
    image = _load_portrait(role)
    if image is None:
        return False
    source_ratio = image.get_width() / image.get_height()
    target_ratio = rect.width / rect.height
    if source_ratio > target_ratio:
        height = image.get_height()
        width = int(height * target_ratio)
        crop = image.subsurface(((image.get_width() - width) // 2, 0, width, height))
    else:
        width = image.get_width()
        height = int(width / target_ratio)
        crop = image.subsurface((0, (image.get_height() - height) // 2, width, height))
    scaled = pygame.transform.smoothscale(crop, rect.size)
    surface.blit(scaled, rect)
    pygame.draw.rect(surface, colors["yellow"] if selected else colors["border"], rect, 3, border_radius=8)
    return True


PALETTE = {
    "be": ((75, 105, 170), (224, 178, 142), (38, 44, 62)),
    "fe": ((177, 93, 151), (236, 190, 153), (44, 37, 62)),
    "qa": ((82, 155, 112), (218, 166, 132), (48, 47, 60)),
    "docs": ((191, 143, 73), (232, 183, 143), (55, 44, 38)),
    "customer": ((157, 108, 180), (231, 180, 146), (51, 42, 67)),
    "support": ((72, 154, 168), (224, 176, 142), (39, 51, 64)),
    "sales": ((180, 85, 81), (236, 190, 154), (48, 40, 52)),
    "ceo": ((67, 76, 132), (238, 191, 157), (44, 37, 58)),
    "accounting": ((104, 103, 116), (221, 170, 135), (43, 43, 52)),
    "legacy": ((117, 65, 126), (185, 132, 110), (35, 27, 46)),
}


def _face(surface, center, scale, role, colors, expression="neutral"):
    x, y = center
    shirt, skin, hair = PALETTE.get(role, PALETTE["be"])
    outline = (24, 27, 36)
    r = int(42 * scale)
    pygame.draw.ellipse(surface, outline, (x - r - 3, y - r - 3, (r + 3) * 2, (r + 3) * 2))
    pygame.draw.ellipse(surface, skin, (x - r, y - r, r * 2, r * 2))
    # Hair and role-specific facial features.
    pygame.draw.arc(surface, hair, (x - r, y - r - 5, r * 2, int(r * 1.35)), 3.1, 6.25, max(3, int(7 * scale)))
    eye_y = y - int(7 * scale)
    pygame.draw.ellipse(surface, (35, 38, 48), (x - int(18 * scale), eye_y, int(8 * scale), int(5 * scale)))
    pygame.draw.ellipse(surface, (35, 38, 48), (x + int(10 * scale), eye_y, int(8 * scale), int(5 * scale)))
    pygame.draw.line(surface, hair, (x - int(20 * scale), eye_y - int(8 * scale)), (x - int(8 * scale), eye_y - int(10 * scale)), max(2, int(4 * scale)))
    pygame.draw.line(surface, hair, (x + int(8 * scale), eye_y - int(10 * scale)), (x + int(20 * scale), eye_y - int(8 * scale)), max(2, int(4 * scale)))
    pygame.draw.line(surface, (160, 104, 88), (x, y - int(3 * scale)), (x - int(3 * scale), y + int(10 * scale)), max(2, int(2 * scale)))
    mouth_y = y + int(22 * scale)
    if expression in {"happy", "proud"}:
        pygame.draw.arc(surface, (114, 46, 53), (x - int(15 * scale), mouth_y - int(8 * scale), int(30 * scale), int(18 * scale)), 0.2, 2.9, max(2, int(3 * scale)))
    elif expression in {"angry", "panic"}:
        pygame.draw.line(surface, (114, 46, 53), (x - int(13 * scale), mouth_y), (x + int(13 * scale), mouth_y), max(2, int(3 * scale)))
    else:
        pygame.draw.arc(surface, (114, 46, 53), (x - int(11 * scale), mouth_y - int(3 * scale), int(22 * scale), int(10 * scale)), 0.2, 2.9, max(2, int(2 * scale)))
    if role == "be":
        pygame.draw.arc(surface, hair, (x - r + 4, y + 2, r * 2 - 8, r + 16), 0.15, 2.95, max(3, int(6 * scale)))
    if role == "fe":
        pygame.draw.rect(surface, hair, (x - int(26 * scale), eye_y - 2, int(22 * scale), int(12 * scale)), 2, border_radius=4)
        pygame.draw.rect(surface, hair, (x + int(4 * scale), eye_y - 2, int(22 * scale), int(12 * scale)), 2, border_radius=4)
        pygame.draw.line(surface, hair, (x - 4, eye_y + 4), (x + 4, eye_y + 4), max(2, int(2 * scale)))
    if role == "qa":
        pygame.draw.arc(surface, (83, 91, 108), (x - r + 2, eye_y - 5, r * 2 - 4, int(27 * scale)), 3.35, 6.05, max(2, int(3 * scale)))
    if role == "ceo":
        pygame.draw.circle(surface, (238, 196, 74), (x + int(29 * scale), y - int(34 * scale)), max(2, int(5 * scale)))
    return shirt


def draw_person(surface, center, scale, role, colors, selected=False):
    x, y = center
    shirt = _face(surface, (x, y - int(17 * scale)), scale * 0.55, role, colors)
    outline = colors["yellow"] if selected else (22, 26, 34)
    s = scale
    pygame.draw.ellipse(surface, outline, (x - 27 * s, y + 25 * s, 54 * s, 22 * s))
    pygame.draw.rect(surface, outline, (x - 26 * s, y + 2 * s, 52 * s, 46 * s), border_radius=max(1, int(12 * s)))
    pygame.draw.rect(surface, shirt, (x - 22 * s, y + 5 * s, 44 * s, 40 * s), border_radius=max(1, int(10 * s)))
    skin = PALETTE.get(role, PALETTE["be"])[1]
    pygame.draw.line(surface, skin, (x - 27 * s, y + 12 * s), (x - 39 * s, y + 28 * s), max(2, int(5 * s)))
    pygame.draw.line(surface, skin, (x + 27 * s, y + 12 * s), (x + 39 * s, y + 28 * s), max(2, int(5 * s)))


def draw_portrait(surface, center, scale, role, colors, expression="neutral"):
    """Крупный портрет лица для диалогового экрана."""
    x, y = center
    y += int(math.sin(pygame.time.get_ticks() / 650) * 2)
    avatar_rect = pygame.Rect(int(x - 105 * scale), int(y - 135 * scale), int(210 * scale), int(265 * scale))
    if draw_avatar(surface, avatar_rect, role, colors, True):
        return
    shirt = _face(surface, (x, y - int(10 * scale)), scale, role, colors, expression)
    pygame.draw.ellipse(surface, (22, 26, 34), (x - int(78 * scale), y + int(55 * scale), int(156 * scale), int(110 * scale)))
    pygame.draw.ellipse(surface, shirt, (x - int(70 * scale), y + int(58 * scale), int(140 * scale), int(100 * scale)))
