import pygame as g
from pygame import Rect, Surface
from pygame.event import Event
from typing import List, Callable

from icons import *
from draw import draw, write
import draw as d


class Widget:
    def __init__(self):
        pass

    def render(self, screen):
        pass

    def event(self, e: Event):
        pass


class Button(Widget):
    MIN = 40

    def __init__(self, left, top, width=MIN, height=MIN, text=None, border='#000000', bw=2, icon=None, iw=1,
                 command=None, icf=d.letters):
        super().__init__()
        self.left = left
        self.top = top
        self.rect = Rect(left, top, width, height)
        self.text = text
        self.border = border
        self.bw = bw
        self.iw = iw
        self.icon = icon
        self.icf = icf
        self.command: Callable = command

    def render(self, screen: Surface):
        w, h = screen.get_size()
        if self.left < 0:
            self.rect.left = w + self.left
        if self.top < 0:
            self.rect.top = h + self.top
        self.rect = g.draw.rect(screen, self.border, self.rect, width=self.bw)
        draw(screen, self.icon, self.rect.left, self.rect.top, self.border, width=self.iw, font=self.icf)
        if self.text:
            write(screen, self.rect.midbottom[0], self.rect.midbottom[1] + 7, self.text, self.border, font=d.tip)

    def event(self, e: Event):
        if e.type == g.MOUSEBUTTONDOWN:
            if e.button == 1:
                if self.rect.collidepoint(*e.pos):
                    self.command()
                    return True
