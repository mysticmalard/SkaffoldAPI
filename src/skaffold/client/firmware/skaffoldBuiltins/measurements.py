# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 MysticMalard

from ..decos import *
from enum import IntEnum, global_enum

Direction = IntEnum('Direction', map(lambda x: x[::-1], enumerate(('RIGHT', 'UP', 'LEFT', 'DOWN',))))
Direction(0)._add_alias_('HORIZONTAL')
Direction(1)._add_alias_('VERTICAL')
global_enum(Direction)

__all__ = ['Direction', 'HORIZONTAL', 'VERTICAL', 'RIGHT', 'UP', 'LEFT', 'DOWN']