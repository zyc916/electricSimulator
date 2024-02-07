import pygame as g

g.font.init()
letters = g.font.SysFont(['timesnewroman', 'simsun', 'microsoftyahei'], 15)
tip = g.font.SysFont(['microsoftyahei', 'simsun'], 12)
chinese = g.font.SysFont(['microsoftyahei', 'simsun'], 15)
title = g.font.SysFont(['microsoftyahei', 'simsun'], 20)


def write(screen, x, y, text, color='#000000', align='center', font=letters):
    w, h = screen.get_size()
    if x < 0:
        x += w
    if y < 0:
        y += h
    s = font.render(text, True, color)
    w, h = font.size(text)
    if align == 'center':
        screen.blit(s, (x - w / 2, y - h / 2))
    elif align == 'left':
        screen.blit(s, (x, y))
    elif align == 'right':
        screen.blit(s, (x - w, y))


def draw(screen, icon, x=0, y=0, color='#000000', width=1, scale=1, font=letters):
    if not icon:
        return False
    if isinstance(icon, dict):
        x -= icon['w'] / 2
        y -= icon['h'] / 2
        icon = icon['i']
    i = 0
    points = []
    while i < len(icon):
        command = icon[i]
        if command == 0 or command == 1:
            g.draw.lines(screen, color, bool(command), points, width)
            points = []
        elif command == 3:
            g.draw.aalines(screen, color, False, points, width)
            points = []
        elif command == 10:
            cir = icon[i - 1]
            g.draw.circle(screen, color, (x + cir[0], y + cir[1]), cir[2], width)
            points = []
        elif isinstance(command, str):
            p = icon[i - 1]
            write(screen, x + p[0], y + p[1], command, font=font, color=color)
            points = []
        else:
            points.append((x + icon[i][0] * scale, y + icon[i][1] * scale))
        i += 1
    if points:
        g.draw.lines(screen, color, False, points)
    return True
