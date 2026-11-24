import pygame


class Button:
    def __init__(self, rect, text, callback, accent=(64, 132, 190)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.accent = accent
        self.hover = False

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.callback()

    def draw(self, surface, font, colors):
        fill = colors["accent"] if self.hover else self.accent
        pygame.draw.rect(surface, fill, self.rect, border_radius=8)
        pygame.draw.rect(surface, colors["border"], self.rect, 2, border_radius=8)
        text = font.render(self.text, True, colors["text"])
        surface.blit(text, text.get_rect(center=self.rect.center))


def text(surface, value, position, font, color, center=False):
    rendered = font.render(str(value), True, color)
    rect = rendered.get_rect(center=position) if center else rendered.get_rect(topleft=position)
    surface.blit(rendered, rect)
    return rect


def panel(surface, rect, colors, fill=None):
    pygame.draw.rect(surface, fill or colors["panel"], rect, border_radius=12)
    pygame.draw.rect(surface, colors["border"], rect, 2, border_radius=12)


def bar(surface, rect, value, maximum, color, colors):
    pygame.draw.rect(surface, colors["panel_light"], rect, border_radius=5)
    width = int(rect.width * max(0, min(value, maximum)) / maximum)
    pygame.draw.rect(surface, color, (rect.x, rect.y, width, rect.height), border_radius=5)
    pygame.draw.rect(surface, colors["border"], rect, 1, border_radius=5)
