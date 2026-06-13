# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 MysticMalard

prevglobs = {}
prevglobs = dict(globals())
from .skaffoldBuiltins import *
newglobs = dict(globals())
_builtins = {}
for glob in newglobs:
    if glob not in prevglobs:
        _builtins[glob] = newglobs[glob]
from .decos import *