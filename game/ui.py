import pygame


_BACKGROUND_CACHE = {}
_GRADIENT_CACHE = {}


def _blend(first, second, ratio):
    return tuple(int(start + (end - start) * ratio) for start, end in zip(first, second))


def gradient_background(surface, colors):
    size = surface.get_size()
    key = (size, colors["bg"], colors["accent"], colors["purple"])
    background = _BACKGROUND_CACHE.get(key)
    if background is None:
        width, height = size
        background = pygame.Surface(size)
        top = _blend(colors["bg"], colors["accent"], 0.12)
        bottom = _blend(colors["bg"], colors["purple"], 0.12)
        for y in range(height):
            pygame.draw.line(background, _blend(top, bottom, y / max(1, height - 1)), (0, y), (width, y))
        glow = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.circle(glow, (*colors["accent"], 22), (width, 0), int(height * 0.8))
        pygame.draw.circle(glow, (*colors["purple"], 22), (0, height), int(height * 0.75))
        background.blit(glow, (0, 0))
        _BACKGROUND_CACHE[key] = background
    surface.blit(background, (0, 0))


def _gradient_surface(size, top, bottom, radius):
    key = (size, top, bottom, radius)
    gradient = _GRADIENT_CACHE.get(key)
    if gradient is None:
        width, height = size
        gradient = pygame.Surface(size, pygame.SRCALPHA)
        for y in range(height):
            pygame.draw.line(gradient, _blend(top, bottom, y / max(1, height - 1)), (0, y), (width, y))
        mask = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
        gradient.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        _GRADIENT_CACHE[key] = gradient
    return gradient


def _shade(color, amount):
    return tuple(max(0, min(255, int(channel * amount))) for channel in color)


def wrap_text(value, font, max_width):
    words = str(value).split()
    lines, current = [], ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


class Button:
    def __init__(self, rect, text, callback, accent=(64, 132, 190), tooltip=None, enabled=True):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.accent = accent
        self.tooltip = tooltip
        self.enabled = enabled
        self.hover = False
        self.selected = False

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif self.enabled and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.callback()

    def draw(self, surface, font, colors):
        if not self.enabled:
            fill = (62, 69, 88)
        elif self.selected:
            fill = colors["green"]
        else:
            fill = colors["accent"] if self.hover else self.accent
        top = _blend(fill, (255, 255, 255), 0.17) if self.enabled else fill
        bottom = _shade(fill, 0.76) if self.enabled else fill
        surface.blit(_gradient_surface(self.rect.size, top, bottom, 8), self.rect.topleft)
        pygame.draw.rect(surface, colors["border"], self.rect, 2, border_radius=8)
        lines = wrap_text(self.text, font, self.rect.width - 18)
        line_height = font.get_linesize()
        start_y = self.rect.centery - (len(lines) - 1) * line_height // 2
        for index, line in enumerate(lines):
            rendered = font.render(line, True, colors["text"])
            color = colors["muted"] if not self.enabled else colors["text"]
            rendered = font.render(line, True, color)
            surface.blit(rendered, rendered.get_rect(center=(self.rect.centerx, start_y + index * line_height)))


def text(surface, value, position, font, color, center=False, max_width=None, line_gap=4):
    lines = wrap_text(value, font, max_width) if max_width else [str(value)]
    line_height = font.get_linesize() + line_gap
    total_height = len(lines) * line_height - line_gap
    for index, line in enumerate(lines):
        rendered = font.render(line, True, color)
        if center:
            rect = rendered.get_rect(center=(position[0], position[1] - total_height // 2 + index * line_height + line_height // 2))
        else:
            rect = rendered.get_rect(topleft=(position[0], position[1] + index * line_height))
        surface.blit(rendered, rect)
    return pygame.Rect(position[0], position[1], max((font.size(line)[0] for line in lines), default=0), total_height)


def panel(surface, rect, colors, fill=None):
    fill = fill or colors["panel"]
    top = _blend(fill, (255, 255, 255), 0.08)
    bottom = _shade(fill, 0.82)
    surface.blit(_gradient_surface(rect.size, top, bottom, 12), rect.topleft)
    pygame.draw.rect(surface, colors["border"], rect, 2, border_radius=12)


def bar(surface, rect, value, maximum, color, colors):
    pygame.draw.rect(surface, colors["panel_light"], rect, border_radius=5)
    width = int(rect.width * max(0, min(value, maximum)) / maximum)
    pygame.draw.rect(surface, color, (rect.x, rect.y, width, rect.height), border_radius=5)
    pygame.draw.rect(surface, colors["border"], rect, 1, border_radius=5)


def tooltip(surface, message, position, font, colors, max_width=300):
    lines = wrap_text(message, font, max_width - 24)
    line_height = font.get_linesize()
    width = min(max_width, max(font.size(line)[0] for line in lines) + 24)
    height = len(lines) * line_height + 18
    x = max(8, min(position[0], surface.get_width() - width - 8))
    y = max(8, min(position[1], surface.get_height() - height - 8))
    box = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (21, 25, 33), box, border_radius=8)
    pygame.draw.rect(surface, colors["accent"], box, 2, border_radius=8)
    for index, line in enumerate(lines):
        text(surface, line, (box.x + 12, box.y + 9 + index * line_height), font, colors["text"])
