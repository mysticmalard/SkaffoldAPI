# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 MysticMalard

from ..decos import *
from .colors import *
from .graphics import *
from .included import *

class Pixel:
    def __init__(self, *pos: tuple[int, int]) -> None:
        self.pos = pos

    def setColor(self, color: Color) -> None:
        # * Funky cuz screen is indexed by [y, x]
        SCREEN[*self.pos[::-1]][:] = color.args

    def getColor(self) -> Color:
        # * Funky cuz screen is indexed by [y, x]
        return Color(*SCREEN[*self.pos[::-1]])

class Row:
    def __init__(self, *pos: tuple[int, int]) -> None:
        self.pixels = (Pixel(x, pos[1]) for x in range(pos[0]))

    def __len__(self) -> int:
        return len(self.pixels)

    def __getitem__(self, key: Key) -> Pixel | tuple[Pixel, ...]:
        return self.pixels[key]

    def __iter__(self) -> iterator:
        return iter(self.pixels)

class SubRow(Row):
    def __init__(self, pos: tuple[int, int], w: int) -> None:
        self.pixels = SCREEN[pos[1]][pos[0]:pos[0]+w]

class Matrix:
    def __init__(self, size: tuple[int, int]) -> None:
        self.rows = (Row(size[0], y) for y in range(size))

    def __getitem__(self, key: Key) -> Pixel | Row | tuple[Pixel | Row, ...]:
        return self.rows[key]

    def __len__(self) -> int:
        return len(self.rows)

    def __iter__(self) -> iterator:
        return iter(self.rows)

class SubMatrix(Matrix):
    def __init__(self, pos: tuple[int, int], size: tuple[int, int]) -> None:
        self.rows = (SubRow((pos[0], y), size[0]) for y in range(pos[1],pos[1]+size[1]))

class Pane:
    def __init__(self, parent: Pane, pos: tuple[int, int], size: tuple[int, int]) -> None:
        self.parent = parent
        self.posX, self.posY = pos
        self.sizeX, self.sizeY = size
        self.graphics: list[Graphic] = []
        self.children: list[Pane] = []
        self.nextCorner: tuple[float, float] = (0.0, 0.0)
        if parent is not None:
            self.matrix = SubMatrix(pos, size)

    def fuse(self) -> None:
        self.parent.children.append(self.children)
        # ! This is probably a dangerous way to do this
        del self

    def fuseChildren(self, recursive: bool = True) -> None:
        for i, child in enum(self.children):
            if recursive:
                self.children.pop(i).fuseChildren(recursive)
            child.fuse()

    def bindGraphic(self, graphic: Graphic) -> None:
        self.graphics.append(graphic)
        graphic.pane = self

    def unbindGraphic(self, i: int) -> Graphic:
        return self.graphics.pop(i)

    def makeChild(self, p2: tuple[int | float, int | float]) -> Pane:
        p2 = list(p2)
        if isinstance(p2[0], float):
            p2[0] = p2[0] * self.sizeX // 1 + self.posX
        if isinstance(p2[1], float):
            p2[1] = p2[1] * self.sizeY // 1 + self.posY
        child = Pane(self, self.nextCorner, (p2[0] - self.nextCorner[0], p2[1] - self.nextCorner[1]))
        self.children.append(child)
        self.nextCorner = p2
        return child

    def render(self) -> None:
        for job in self.graphics + self.children:
            job.render()

    def __getitem__(self, *keys: tuple[Key, ...]) -> Matrix | Row | Pixel | tuple[Pixel | Row, ...]:
        # * Functionally the same but slightly more compact
        # * if len(keys) - 1:
        # *     return self.matrix[keys[0]][keys[1]]
        # * else:
        # *     return self.matrix[keys[0]]
        return (lambda x: x[keys[1]] if (len(keys)-1) else x)(self.matrix[keys[0]])
    
    def __iter__(self) -> iterator:
        return iter(self.matrix)

class Framebuffer:
    def __init__(self, size: tuple[int, int]) -> None:
        self.frames = ((([0, 0, 0],) * size[1],) * size[0], (([0, 0, 0],) * size[1],) * size[0])
        self.flipped = 0

    def __getitem__(self, *keys: tuple[Key, Key | None]) -> tuple[tuple[list[int], ...], ...] | tuple[list[int], ...] | list[int]:
        frame = self.frames[self.flipped]
        for key in keys:
            frame = frame[key]
        return frame

    def __setitem__(self, *keys: tuple[Key, Key | None], value: int) -> None:
        self.frames[not self.flipped][*keys] = value

    def flip(self) -> None:
        self.flipped ^= 1

class Screen(Pane):
    def __init__(self) -> None:
        Pane.__init__(self, None, (0, 0), (size := get_matrix()))
        self.matrix = Matrix(size)
        self.framebuffer = Framebuffer(size)

    def render(self) -> None:
        Pane.render(self)
        self.flip()

    def flip(self) -> None:
        self.framebuffer.flip()
        draw(self.framebuffer[:])

SCREEN = Screen()