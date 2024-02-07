from typing import Union, List, Tuple, Optional, Set, Dict, Type, Callable
import pygame as g
import ctypes
from easygui import msgbox
from numpy.linalg import lstsq

from os import system

from pygame.event import Event
import cells
import draw
from ui import Widget, Button
from icons import *

# Global Area
g.init()
screen = g.display.set_mode((960, 720), flags=g.RESIZABLE)
clock = g.time.Clock()
ctypes.windll.shcore.SetProcessDpiAwareness(2)

out: Optional[Type[cells.Cell]] = None
selected: Optional[cells.Cell] = None

edited = False


def set_type(kind) -> Callable:
    """
    一个高阶函数，返回指定元件的构造函数

    :param kind: 元件类型
    :return: 元件
    """

    def warp():
        global out
        out = object.__getattribute__(cells, kind)

    return warp


class MainUI:
    def __init__(self, s):
        self.screen: g.Surface = s
        self.widgets: List[Widget] = []
        self.temp: List[Widget] = []
        self.widgets.append(Button(10, 10, icon=BATTERY_BUTTON, command=set_type('Battery'), text='电池'))
        self.widgets.append(Button(10, 70, icon=SWITCH_BUTTON, command=set_type('Switch'), text='开关'))
        self.widgets.append(Button(10, 140, icon=RESISTOR_BUTTON, command=set_type('Resistor'), text='定值电阻'))
        self.widgets.append(
            Button(10, 200, icon=RESISTOR_F_BUTTON, command=set_type('ResistorFlexible'), text='滑动变阻器'))
        self.widgets.append(Button(10, 260, icon=RESISTOR_C_BUTTON, command=set_type('ResistorChest'), text='电阻箱'))
        self.widgets.append(Button(10, 330, icon=VOLTAGE_METER_BUTTON, command=set_type('VoltageMeter'), text='电压表'))
        self.widgets.append(Button(10, 390, icon=CURRENT_METER_BUTTON, command=set_type('CurrentMeter'), text='电流表'))

    def render(self):
        for w in self.widgets:
            w.render(self.screen)
        for t in self.temp:
            t.render(self.screen)
        h = self.screen.get_height()
        w = self.screen.get_width()
        g.draw.line(self.screen, '#000000', (60, 0), (60, h))
        g.draw.line(self.screen, '#000000', (w - 200, 0), (w - 200, h))

    def event(self, e: Event):
        global selected, edited
        for w in self.widgets:
            if w.event(e):
                selected = None
                return True
        for w in self.temp:
            if w.event(e):
                edited = True
                return True
        else:
            return False


class CellManager:
    basic_attr = {
        '电压(V)': '_voltage',
        '电流(A)': '_current'
    }

    def __init__(self, s: g.Surface):
        # Important
        self.screen = s
        # Elements
        self.battery: Optional[cells.Battery] = None
        # Gui
        self.select: Optional[cells.Cell] = None
        self.dragging: Optional[cells.Cell] = None
        self.hover: Optional[cells.Extremity] = None
        self.extremity: Optional[cells.Extremity] = None
        # Calc
        self.connected: Set[Union[cells.Cell]] = set()
        self.remain: Set[Union[cells.Cell]] = set()
        self.indexes: List[Union[cells.Cell]] = []
        self.available: Dict[int, bool] = {}
        # KCL & KVL
        self.routes: Set[Tuple] = set()
        self.i_cases: Set[Tuple[int]] = set()
        self.r_cases: Set[Tuple[int]] = set()

    def render(self):
        pos = g.mouse.get_pos()
        if self.hover:
            g.draw.circle(self.screen, '#ff7777', self.hover[0].get_ext(self.hover[1]), 5)
        if self.extremity:
            cells.Wire.render(self.screen, self.extremity, pos)
        if selected:
            change = selected.select_gui(self.screen, window, self.select)
            if change:
                self.select = selected
        else:
            window.temp.clear()
        for cell in cells.Cell.instances.values():
            cell.render_me(self.screen)
        for wire in cells.Wire.instances.values():
            wire.render_me(self.screen)
        if out:
            m = g.mouse.get_pos()
            out.render(self.screen, *m)

    def calc(self):
        if not self.battery:
            return
        self.connected.clear()
        self.connected.add(self.battery)
        self.remain.clear()
        self.indexes.clear()
        self.available.clear()
        self.routes.clear()
        self.i_cases.clear()
        self.r_cases.clear()

        def get_child(cell, side):
            next_ext: Set[cells.Extremity] = set()
            for w in cell.connects[1 - side]:
                for ext in w.ext:
                    next_ext.add(ext)
            rep = 0
            while rep < 3:
                new_ext = set()
                for nex in next_ext.copy():
                    for w in nex[0].connects[nex[1]]:
                        for ext in w.ext:
                            next_ext.add(ext)
                if new_ext - next_ext:
                    rep = 0
                    next_ext |= new_ext
                else:
                    rep += 1
            return next_ext

        def get_connected():
            new = set()
            while True:
                new.clear()
                for cell in self.connected:
                    for cons in cell.connects:
                        for wire in cons:
                            for ext in wire.ext:
                                new.add(ext[0])
                if new - self.connected:
                    self.connected |= new
                else:
                    break
            return

        def dfs(cell, route, side):
            next_ext = get_child(cell, side)
            more = False
            for ext in next_ext:
                if ext[0].resistance == -1:
                    continue
                if ext[0] is self.battery and ext[1] == 1:
                    more = True
                    self.routes.add(tuple(sorted(route.copy() + [(cell, ext[1])], key=lambda x: x[0].id)))
                    continue
                if ext[0] in self.remain:
                    self.remain.remove(ext[0])
                    able = dfs(ext[0], route.copy() + [(cell, 1 - side)], ext[1])
                    if able:
                        more = True
                        self.available[ext[0].id] = True
                    self.remain.add(ext[0])
            return more

        def analysis():
            cou = len(self.connected)
            for cell in self.connected:
                if self.available[cell.id]:
                    for side in range(2):
                        i_case = [0] * cou
                        more = False
                        next_ext = get_child(cell, side)
                        for ext in next_ext:
                            if not self.available[ext[0].id]:
                                continue
                            more = True
                            value = 1 if ext[1] == 1 else -1
                            if ext[0] is self.battery:
                                value = -value
                            i_case[self.indexes.index(ext[0])] = value
                        if more:
                            if tuple(map(lambda x: -x, i_case)) not in self.i_cases:
                                self.i_cases.add(tuple(i_case))
            for rou in self.routes:
                r_case = [0] * cou
                for ex in rou:
                    dire = 1 if ex[1] == 1 else -1
                    if ex[0] is self.battery:
                        dire = -dire
                    r_case[self.indexes.index(ex[0])] = ex[0].resistance * dire
                self.r_cases.add(tuple(r_case))

        get_connected()
        if len(self.connected) == 1:
            return
        self.remain = self.connected.copy()
        self.remain.remove(self.battery)
        self.indexes = list(sorted(self.connected, key=lambda ce: ce.id))
        self.available = dict(zip(map(lambda ce: ce.id, self.connected), (False,) * len(self.connected)))
        dfs(self.battery, [], 1)
        self.available[self.battery.id] = True
        analysis()
        left = list(self.i_cases) + list(self.r_cases)
        right = [[0, ], ] * len(self.i_cases) + [[self.battery.emf, ], ] * len(self.r_cases)
        result = lstsq(left, right, rcond=None)[0]
        for i in range(len(self.indexes)):
            one = cells.Cell.instances[self.indexes[i].id]
            current = round(result[i][0], 7)
            one.current = current

    def event(self, e: Event):
        global out, selected, edited
        w = self.screen.get_width()
        if e.type == g.MOUSEBUTTONDOWN:
            if self.hover:
                self.extremity = self.hover
            else:
                if self.select:
                    if self.select.rect.collidepoint(*e.pos):
                        self.dragging = self.select
                    elif e.pos[0] > w - 200:
                        return True
                selected = None
                self.select = None
                for cell in cells.Cell.instances.values():
                    if cell.rect.collidepoint(*e.pos):
                        selected = cell
                        self.dragging = cell
                    else:
                        cell.selected = False
                if self.dragging:
                    selected.selected = True
        elif e.type == g.MOUSEMOTION:
            for cell in cells.Cell.instances.values():
                h = cell.hovering(*e.pos)
                if h is not None:
                    self.hover = (cell, h)
                    break
            else:
                self.hover = None
            if e.buttons == (1, 0, 0):
                if self.dragging:
                    self.dragging.move(*e.pos)
        elif e.type == g.MOUSEBUTTONUP:
            if self.dragging and e.pos[0] < 60:
                if self.dragging is self.battery:
                    self.battery = None
                if self.dragging is selected:
                    selected = None
                    self.select = None
                self.dragging.delete()
                edited = True
            if out is not None and e.pos[0] > 60:
                if out == cells.Battery:
                    if self.battery:
                        msgbox('由于技术上的问题，目前只能添加一个电源。', '失败')
                    else:
                        self.battery = out(*e.pos)
                        edited = True
                else:
                    out(*e.pos)
                    edited = True
            if self.hover and self.extremity and self.extremity != self.hover:
                wire = cells.Wire(self.extremity, self.hover)
                self.extremity[0].connect(wire, self.extremity[1])
                self.hover[0].connect(wire, self.hover[1])
                edited = True
            out = None
            self.dragging = None
            self.extremity = None
        if edited:
            self.calc()
        for ce in cells.Cell.instances.values():
            if ce.event(e):
                edited = True
                return True

    def clear(self):
        for ce in list(cells.Cell.instances.values()):
            ce.delete()
        self.battery: Optional[cells.Battery] = None
        self.select: Optional[cells.Cell] = None
        self.dragging: Optional[cells.Cell] = None
        self.hover: Optional[cells.Extremity] = None
        self.extremity: Optional[cells.Extremity] = None


window = MainUI(screen)
manager = CellManager(screen)

window.widgets.append(Button(10, -130, command=lambda: system('start notepad ./README.txt'), icon=HELP,
                             border='#00bbee', iw=1, text='使用说明', icf=draw.chinese))
window.widgets.append(Button(10, -60, command=manager.clear, icon=DELETE, border='#dd0000', iw=3, text='全部删除'))


def render_all():
    window.render()
    manager.render()
    g.display.flip()
    screen.fill('#eeeeee')


def main():
    while True:
        clock.tick(60)

        for event in g.event.get():
            # Global Events
            if event.type == g.QUIT:
                exit()
            if not window.event(event):  # UI Events
                # Cell Events
                if not manager.event(event):
                    pass
        render_all()


main()
