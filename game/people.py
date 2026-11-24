import pygame


def draw_person(surface, center, scale, role, colors, selected=False):
    x, y = center
    s = scale
    palette = {
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
    shirt, skin, hair = palette.get(role, palette["be"])
    outline = colors["yellow"] if selected else (22, 26, 34)
    pygame.draw.ellipse(surface, outline, (x - 27 * s, y + 25 * s, 54 * s, 22 * s))
    pygame.draw.rect(surface, outline, (x - 26 * s, y + 2 * s, 52 * s, 46 * s), border_radius=max(1, int(12 * s)))
    pygame.draw.rect(surface, shirt, (x - 22 * s, y + 5 * s, 44 * s, 40 * s), border_radius=max(1, int(10 * s)))
    pygame.draw.circle(surface, skin, (int(x), int(y - 17 * s)), max(1, int(18 * s)))
    pygame.draw.arc(surface, hair, (x - 18 * s, y - 36 * s, 36 * s, 30 * s), 3.25, 6.15, max(2, int(5 * s)))
    pygame.draw.circle(surface, (30, 35, 43), (int(x - 6 * s), int(y - 18 * s)), max(1, int(2 * s)))
    pygame.draw.circle(surface, (30, 35, 43), (int(x + 6 * s), int(y - 18 * s)), max(1, int(2 * s)))
    pygame.draw.line(surface, skin, (x - 27 * s, y + 12 * s), (x - 39 * s, y + 28 * s), max(2, int(5 * s)))
    pygame.draw.line(surface, skin, (x + 27 * s, y + 12 * s), (x + 39 * s, y + 28 * s), max(2, int(5 * s)))
