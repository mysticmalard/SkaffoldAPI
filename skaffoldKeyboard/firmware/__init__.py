prevglobs = {}
prevglobs = dict(globals())
from .skaffoldBuiltins import *
newglobs = dict(globals())
_builtins = {}
for glob in newglobs:
    if glob not in prevglobs:
        _builtins[glob] = newglobs[glob]
from .decos import *