# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 MysticMalard

from .firmware import *

# TODO: REWRITE WITH REGEX

import dis, inspect, annotationlib

def include(device, target, method_of=None):
    if isinstance(target, (alias, union)):
        for arg in target.__args__:
            if arg not in types and arg is not method_of:
                include(device, arg)
    elif target.__class__ not in (type, function):
        include(device, target.__class__)
    elif target.__name__ not in device.deps and target.__name__ not in device.pending and target not in types and target is not method_of:
        if isinstance(target, function):
            if method_of is None and target.__name__ not in device.pending:
                device.pending.append(target.__name__)
            sig = inspect.signature(target, annotation_format=annotationlib.Format.STRING)
            anots = set(map(lambda y: eval(y.annotation),
                set(filter(lambda x: x.annotation is not x.empty,
                            sig.parameters.values())))) | {eval(sig.return_annotation)}
            for anot in anots:
                # function flag bit 0x20 tells if the function is a generator
                # function flag bit 0x04 tells if it uses *args
                # function flag bit 0x08 tells if it uses **kwargs
                if isinstance(anot, (alias, union)):
                    include(device, anot)
                elif anot is None:
                    pass
                elif anot not in types and anot is not method_of:
                    include(device, anot)
            include_funct(device, target, method_of)
            if method_of is None:
                device.deps.append(target.__name__)
                device.pending.pop()
        elif isinstance(target, type):
            if target.__name__ not in device.pending:
                device.pending.append(target.__name__)
            for t in type.mro(target)[1:-1]:
                include(device, t)
            for meth in filter(lambda x: isinstance(x, function), vars(target).values()):
                include(device, meth, target)
            device.deps.append(target.__name__)
            device.pending.pop()

def include_global(device, inst, method_of=None):
    if inst.argval not in device.deps and inst.argval in globals():
        target = globals()[inst.argval]
        if target is not method_of:
            if isinstance(target, (function, type)):
                include(device, target, method_of)
            else:
                include(device, target.__class__)
                if target.__class__.__name__ in device.deps:
                    device.deps.append(inst.argval)

def include_funct(device, foo, method_of=None):
    code = dis.Bytecode(foo)
    insts = iter(code)
    for inst in insts:
        match inst.baseopname:
            case "LOAD_GLOBAL":
                include_global(device, inst, method_of)