# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 MysticMalard

from types import GenericAlias as alias, UnionType as union
from typing import Any, Iterator as iterator, TypeAlias
from enum import Enum, EnumType, ReprEnum, IntEnum, global_enum

from ..decos import *
from .colors import *
from .measurements import Direction, HORIZONTAL, VERTICAL, RIGHT, UP, LEFT, DOWN
from .graphics import *
from .panel import Pane

function: TypeAlias = type(lambda: None)

types = [
    Any,
    alias,
    bool,
    dict,
    EnumType,
    IntEnum,
    ReprEnum,
    Enum,
    type(Ellipsis),
    Ellipsis,
    enumerate,
    filter,
    float,
    function,
    int,
    iterator,
    list,
    map,
    memoryview,
    None,
    type(None),
    object,
    range,
    reversed,
    set,
    slice,
    str,
    super,
    tuple,
    type,
    union,
    zip,
]

enums = [
    Direction
]

funcs = [
    global_enum,
    all,
    any,
    isinstance,
    issubclass,
    iter,
    len,
    next
]

@_kern
@_op
def reply(data: tuple[int, ...]) -> None:
    ...

@_kern('read')
@_op('read')
def listen(argc: int, wait: bool = True) -> tuple[int, ...]:
    ...

@_kern
@_op
def delay(t: int) -> None:
    ...

@_kern
@_op('sys')
def sys_call() -> None:
    ...

@_kern
@_op('rebt')
def reboot() -> None:
    ...

@_op
def lerp(t: float, a: Any, b: Any) -> Any:
    return (1 - t) * a + t * b

@_op
def delerp(v: float, a: float, b: float) -> float:
    # * Shoutout to Freya Holmer for the delerp
    return (v - a) / (b - a)

@_op
def scale(p1: tuple[Color, float], p2: tuple[Color, float], alpha: float) -> Color:
    # * Shoutout to Freya Holmer for the rescale
    return lerp(delerp(alpha, p1[1], p2[1]), p1[0], p2[0])

@_op
def charToFloat(val: int, signed: bool = False) -> float:
    v = val ^ (((val & 128) << 1) - signed)
    return v / 256

@_kern
@_op
def draw(frame: tuple[tuple[list[int, int, int], ...], ...]) -> None:
    ...

@_op
def bisect(parent: Pane, size: int | float, direction: Direction = HORIZONTAL) -> tuple[Pane, Pane]:
    s = (size, 1.0) if direction&1 else (1.0, size)
    child1 = parent.makeChild(s)
    child2 = parent.makeChild((1.0, 1.0))
    return child1, child2

@_op
def partition(parent: Pane, num: int, direction: Direction = HORIZONTAL) -> tuple[Pane, ...]:
    s = 1 / num
    children = list(bisect(parent, s, direction))
    subparent = children[1]
    for i in range(num - 1):
        children.append(bisect(children.pop(), s, direction))
    subparent.fuseChildren()
    subparent.fuse()
    return tuple(children)