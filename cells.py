from operator import xor
from typing import Union, List, Tuple

import pygame as g
from pygame import Surface

from draw import *
from icons import *
from ui import Button


def add_value(cell, name, value):
    def warp():
        attr = cell.__getattribute__(name)
        if value < 0:
            if attr >= abs(value):
                cell.__setattr__(name, attr + value)
        else:
            cell.__setattr__(name, attr + value)

    return warp


class Cell:
    basic_attr = {
        'ID': 'id',
        '电压(V)': '_voltage',
        '电流(A)': '_current'
    }
    arguments = {
        '电阻(Ω)': '_resistance'
    }
    name = '元件'
    symbol = '?'
    symbol_trans = -20
    icon = None
    b_icon = None
    id = 0
    instances = {}

    def __init__(self, x: int, y: int, resistance, border='#000000'):
        Cell.id += 1
        Cell.instances[Cell.id] = self
        self.id = Cell.id
        self.state = 1

        self.x = x
        self.y = y
        self.rect: g.Rect = g.Rect(x, y, 0, 0)
        self.border = border

        self._resistance = resistance
        self._voltage = 0
        self._current = 0
        self.move(x, y)

        self.selected = 0
        self.connects: List[List[Wire]] = [[], []]

    def __str__(self):
        return self.__class__.__name__ + str(self.id)

    def __repr__(self):
        return self.__class__.__name__ + str(self.id)

    def delete(self):
        self.state = -1
        for cons in self.connects:
            for w in cons:
                w.delete()

        self.connects = []
        if self.id in Cell.instances:
            Cell.instances.pop(self.id)

    __del__ = delete

    def move(self, x, y):
        self.x, self.y = x, y
        if self.rect:
            self.rect.centerx, self.rect.centery = x, y
        else:
            if self.icon:
                self.rect = g.Rect(0, 0, self.icon['w'], self.icon['h'])
            else:
                self.rect = g.Rect(0, 0, 0, 0)
            self.rect.centerx = x
            self.rect.centery = y

    def connect(self, wire, side):
        self.connects[side].append(wire)

    def get_ext(self, side):
        return (self.rect.right + 5, self.rect.centery) if side == 1 else (self.rect.left - 5, self.rect.centery)

    def hovering(self, x, y):
        for side in range(2):
            x0, y0 = self.get_ext(side)
            if abs(x - x0) + abs(y - y0) < 5:
                return side
        else:
            return None

    def event(self, event) -> bool:
        return False

    @classmethod
    def render(cls, screen: Surface, x, y, color='#000000', state=0, icon=None, width=1):
        write(screen, x, y + cls.symbol_trans, cls.symbol, color)
        i = None
        if icon:
            i = icon
        elif cls.icon:
            i = cls.icon
        if i:
            draw(screen, i, x, y, color, width)

    def render_me(self, screen: Surface):
        if self.selected:
            self.render(screen, self.x, self.y, color='#aaaaaa', state=self.state, width=3)
        self.render(screen, self.x, self.y, self.border, self.state)

    def select_gui(self, screen, window, last):
        if last is not self:
            window.temp.clear()
        w = screen.get_width()
        change = False
        x = w - 200
        y_pos = 60
        g.draw.rect(screen, '#000000', g.Rect(x + 10, 10, 40, 40), width=2)
        draw(screen, self.b_icon, x + 10, 10)
        write(screen, -130, 15, self.name, align='left', font=title)
        for name, attr in self.basic_attr.items():
            write(screen, -180, y_pos, name, align='left', font=chinese)
            write(screen, -20, y_pos, str(round(self.__getattribute__(attr), 7)), align='right', font=chinese)
            y_pos += 30
        y_pos += 30
        for name, attr in self.__class__.arguments.items():
            write(screen, -180, y_pos, name, align='left', font=chinese)
            write(screen, -60, y_pos, str(round(self.__getattribute__(attr), 7)), align='right', font=chinese)
            if last is not self:
                window.temp.append(
                    Button(-20, y_pos, width=20, height=20, icon=ADD, command=add_value(self, attr, 1)))
                window.temp.append(
                    Button(-50, y_pos, width=20, height=20, icon=MINUS, command=add_value(self, attr, -1)))
                change = True
            y_pos += 30
        return change

    @property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, voltage):
        self._voltage = voltage
        self._current = voltage / self._resistance

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, current):
        self._voltage = current * self.resistance
        self._current = current

    @property
    def resistance(self):
        return self._resistance


class Node:
    def __init__(self, lines: List, x, y):
        self.lines = lines
        self.x = x
        self.y = y

    def get_ext(self):
        return self.x, self.y


Pos = Tuple[float, float]
Extremity = Tuple[Union[Cell], int]


class Wire:
    resistance = 0
    h_dis = 40
    border_min = 20
    id = 0
    instances = {}

    def __init__(self, f: Extremity, t: Extremity):
        Wire.id += 1
        Wire.instances[Wire.id] = self
        self.id = Wire.id
        self.state = 1

        self.ext = {f, t}
        self.selected = False

    def delete(self):
        self.state = -1
        self.ext = {}
        if self.id in Wire.instances:
            Wire.instances.pop(self.id)

    __del__ = delete

    @classmethod
    def render(cls, screen, f: Extremity, t: Union[Extremity, Pos]):
        fp = f[0].get_ext(f[1])
        if isinstance(t[0], (float, int)):
            side = abs(fp[1] - t[1]) < cls.h_dis
            tp = t
        else:
            side = f[1] + t[1]
            tp = t[0].get_ext(t[1])
            if f[0] is t[0]:
                g.draw.lines(screen, '#000000', False, [fp, (fp[0], fp[1] + 20), (tp[0], tp[1] + 20), tp])
                return
        if side != 1:
            lr = -1 if f[1] == 0 else 1
            if xor(f[1] > 0, fp[0] > tp[0]):
                x = tp[0] + cls.border_min * lr
            else:
                x = fp[0] + cls.border_min * lr
        else:
            if xor(f[1] > 0, fp[0] < tp[0]):
                y = (tp[1] + fp[1])/2
                g.draw.lines(screen, '#000000', False, [fp, (fp[0], y), (tp[0], y), tp])
                return
            else:
                x = (fp[0] + tp[0]) / 2
        g.draw.lines(screen, '#000000', False, [fp, (x, fp[1]), (x, tp[1]), tp])

    def render_me(self, screen):
        self.render(screen, *self.ext)


class Battery(Cell):
    arguments = {
        '内阻(Ω)': '_resistance',
        '电动势(V)': 'emf'
    }
    name = '电池'
    symbol = 'E'
    symbol_trans = -25
    icon = Battery_0
    b_icon = BATTERY_BUTTON

    def __init__(self, x, y, emf=3, resistance=0, positive_side=0):
        """

        :param emf: The `Electromotive Force` of the battery
        :param resistance:
        :param positive_side:
        """
        super().__init__(x, y, resistance)
        self.emf = emf
        self.positive_side = positive_side

    @property
    def resistance(self):
        return self._resistance


class Switch(Cell):
    name = '开关'
    symbol = 'S'
    symbol_trans = -20
    icon = Switch_0
    b_icon = SWITCH_BUTTON

    def __init__(self, x, y, resistance=0):
        super().__init__(x, y, resistance)  # 导通电阻
        self.state = 0

    def switch(self):
        self.state = 1 - self.state

    @property
    def resistance(self):
        if self.state == 1:
            return self._resistance
        else:
            return -1

    def event(self, event) -> bool:
        if event.type == g.MOUSEBUTTONDOWN:
            if self.selected:
                if self.rect.collidepoint(*event.pos):
                    self.switch()
                    return True
        return False

    @classmethod
    def render(cls, screen: Surface, x, y, color='#000000', state=0, icon=None, width=1):
        if state == 0:
            super().render(screen, x, y, color, state, Switch_0)
        else:
            super().render(screen, x, y, color, state, Switch_1)


class Resistor(Cell):
    arguments = {
        '电阻(Ω)': '_resistance',
    }
    name = '定值电阻'
    symbol = 'R'
    symbol_trans = -20
    icon = Resistor_0
    b_icon = RESISTOR_BUTTON

    def __init__(self, x, y, resistance=10):
        super().__init__(x, y, resistance)


class ResistorFlexible(Cell):
    basic_attr = {
        'ID': 'id',
        '电压(V)': '_voltage',
        '电流(A)': '_current',
        '当前电阻(Ω)': 'resistance'
    }
    arguments = {
        '最大电阻(Ω)': 'max_resistance',
    }
    name = '滑动变阻器'
    symbol = 'Rf'
    symbol_trans = -30
    icon = ResistorFlexible_0
    b_icon = RESISTOR_F_BUTTON

    def __init__(self, x, y, max_resistance=10, available=40, length=40):
        super().__init__(x, y, max_resistance)
        self.state = False
        self.max_resistance = max_resistance
        self.available = available
        self.length = length

    def drag(self, pos):
        if not self.selected:
            if self.state:
                if self.rect.left <= pos[0] <= self.rect.right:
                    self.available = pos[0] - self.rect.left
                elif pos[0] > self.rect.right:
                    self.available = self.length
                else:
                    self.available = 0
        return self.state

    def event(self, event) -> bool:
        if event.type == g.MOUSEBUTTONDOWN:
            if abs(event.pos[1] - self.rect.top) < 10 and self.rect.left <= event.pos[0] <= self.rect.right:
                self.state = True
                self.drag(event.pos)
            return self.state
        elif event.type == g.MOUSEMOTION:
            if event.buttons == (1, 0, 0) and self.state:
                return self.drag(event.pos)
        elif event.type == g.MOUSEBUTTONUP:
            self.state = False
        return False

    def get_ext(self, side):
        if side == 1:
            return self.rect.centerx, self.rect.top - 10
        else:
            return self.rect.left - 5, self.rect.centery

    def render_me(self, screen: Surface):
        super().render_me(screen)
        y0 = self.rect.top - 5
        vl = self.rect.left + self.available
        write(screen, vl, y0 - 10, str(self.resistance), font=tip)
        g.draw.lines(screen, self.border, False, [(self.rect.centerx, y0), (vl, y0), (vl, y0 + 5), (vl - 2, y0 + 2)])
        g.draw.lines(screen, self.border, False, [(vl, y0 + 5), (vl + 2, y0 + 2)])

    @property
    def resistance(self):
        return self.max_resistance * self.available / self.length


class ResistorChest(Cell):
    basic_attr = {
        'ID': 'id',
        '电压(V)': '_voltage',
        '电流(A)': '_current',
        '当前电阻(Ω)': 'resistance'
    }
    arguments = {}
    name = '电阻箱'
    symbol = 'Rc'
    symbol_trans = -30
    icon = ResistorChest_0
    b_icon = RESISTOR_C_BUTTON

    def __init__(self, x, y, max_resistance=9999, division=1):
        super().__init__(x, y, max_resistance)
        self._resistance = 0
        self.max_resistance = max_resistance
        self.division = division

    @property
    def resistance(self):
        return self._resistance

    def render_me(self, screen: Surface):
        super().render_me(screen)
        write(screen, self.rect.centerx, self.rect.top - 10, str(self.resistance), font=tip)

    def select_gui(self, screen, window, last):
        w, h = screen.get_size()
        super().select_gui(screen, window, last)
        g.draw.line(screen, '#000000', (w - 200, h - 130), (w, h - 130))
        write(screen, -150, -100, str(int(self._resistance // 1000)))
        write(screen, -50, -100, str(int(self._resistance % 1000 // 100)))
        write(screen, -150, -50, str(int(self._resistance % 100 // 10)))
        write(screen, -50, -50, str(int(self._resistance % 10 // 1)))
        write(screen, -150, -80, 'x1000')
        write(screen, -50, -80, 'x100')
        write(screen, -150, -30, 'x10')
        write(screen, -50, -30, 'x1')

        change = False
        if last is not self:
            window.temp.append(Button(-180, -110, width=20, height=20, icon=MINUS,
                                      command=add_value(self, '_resistance', -1000)))
            window.temp.append(Button(-140, -110, width=20, height=20, icon=ADD,
                                      command=add_value(self, '_resistance', 1000)))

            window.temp.append(Button(-80, -110, width=20, height=20, icon=MINUS,
                                      command=add_value(self, '_resistance', -100)))
            window.temp.append(Button(-40, -110, width=20, height=20, icon=ADD,
                                      command=add_value(self, '_resistance', 100)))

            window.temp.append(Button(-180, -60, width=20, height=20, icon=MINUS,
                                      command=add_value(self, '_resistance', -10)))
            window.temp.append(Button(-140, -60, width=20, height=20, icon=ADD,
                                      command=add_value(self, '_resistance', 10)))

            window.temp.append(Button(-80, -60, width=20, height=20, icon=MINUS,
                                      command=add_value(self, '_resistance', -1)))
            window.temp.append(Button(-40, -60, width=20, height=20, icon=ADD,
                                      command=add_value(self, '_resistance', 1)))
            change = True
        return change


class Meter(Cell):
    icon = Meter_0

    def __init__(self, x, y, resistance=200, span=0.1):
        super().__init__(x, y, resistance)
        self.span = span

    def render_me(self, screen: Surface):
        super().render_me(screen)
        value = round(self.value, 7)
        if -self.span <= value <= self.span:
            write(screen, self.x, self.y - 20, str(value))
        elif value > self.span:
            write(screen, self.x, self.y - 20, '>' + str(self.span))
        else:
            write(screen, self.x, self.y - 20, '<' + str(-self.span))

    @property
    def value(self):
        return self.current


class VoltageMeter(Meter):
    arguments = {
        '阻值(Ω)': '_resistance',
        '量程(V)': 'span'
    }
    name = '电压表'
    symbol = 'V'
    symbol_trans = 0
    b_icon = VOLTAGE_METER_BUTTON

    def __init__(self, x, y, resistance=500, span=3):
        super().__init__(x, y, resistance, span)

    @property
    def value(self):
        return self.voltage


class CurrentMeter(Meter):
    arguments = {
        '阻值(Ω)': '_resistance',
        '量程(A)': 'span'
    }
    name = '电流表'
    symbol = 'A'
    symbol_trans = 0
    b_icon = CURRENT_METER_BUTTON

    def __init__(self, x, y, resistance=0, span=3):
        super().__init__(x, y, resistance, span)
