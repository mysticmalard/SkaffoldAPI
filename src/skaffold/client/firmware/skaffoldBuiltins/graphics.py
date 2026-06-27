# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 MysticMalard

from ..decos import *
from .colors import *
from .measurements import *
from .included import *

class Graphic:
    def __init__(self) -> None:
        self.pane = None

    def render(self) -> None:
        pass

class Gradient:
    def __init__(self, *points: tuple[tuple[Color, float], ...]) -> None:
        self.points = list(points)

    def getColor(self, alpha: float) -> Color:
        for i in range(len(self.points)):
            if (p := self.points[i])[1] >= alpha:
                break
        return scale(self.points[i-1], p, alpha)

class SimpleGradient(Gradient):
    def __init__(self, color1: Color, color2: Color) -> None:
        Gradient.__init__(self, (color1, 0.0), (color2, 1.0))

class Bar(Graphic):
    def __init__(self, direction: Direction, gradient: Gradient, solid: bool = True, signed: bool = False) -> None:
        Graphic.__init__(self)
        self.direction = direction
        self.gradient = gradient
        self.isSolid = solid
        self.alpha: float = 0.0
        self.isSigned = signed

    def setAlpha(self, t: int | float) -> None:
        if isinstance(t, float):
            self.alpha = t
        else:
            self.alpha = charToFloat(t, self.isSigned)

    def changeGradient(self, newGrad: Gradient) -> None:
        self.gradient = newGrad

    def render(self) -> None:
        for y in range((h := len(self.pane))):
            l = h if self.direction&1 else (w := len(self.pane[y]))
            for x in range(w):
                i = y if self.direction&1 else x
                c = self.gradient.getColor(self.alpha) if self.solid else self.gradient.getColor(i / l)
                if (i <= self.alpha) ^ (self.direction>>1):
                    self.pane[y][x].setColor(c)
                else:
                    self.pane[y][x].setColor(BLACK)