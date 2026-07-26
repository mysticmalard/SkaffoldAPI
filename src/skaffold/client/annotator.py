# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 MysticMalard

from .firmware import *

from .translator import *

import inspect, annotationlib, regex

def parse_anot(device, anot: str, method_of=None):
    if anot == 'None':
        device.app('hint Void')
    elif anot == '...':
        device.app('hint Ellipsis')
    elif anot == 'iterator':
        device.app('hint iter')
    elif regex.match(r"^\w+$", anot):
        if method_of and anot is method_of.__name__:
            device.app('hint Self')
        else:
            device.app(f'hint {anot}')
    # * duck.ai wrote that regex :/
    # * ALL OTHERS ARE MINE UNLESS OTHERWISE STATED
    # * Sorry, I'm proud of myself cuz regex looks like keyboard spam
    elif regex.search(r'(?<![^\[\]]*\[)\|(?!(?:[^\[\]]*\]))', anot) is not None:
        # * duck.ai wrote this one
        args = regex.split(r'\s*\|\s*(?![^\[\]]*\])', anot)
        device.app('hint union')
        for i, arg in enumerate(args):
            parse_anot(device, arg, method_of)
        device.app(f'imm {i+1}', 'tuple', 'anot')
    elif (x := regex.findall(r'^\w+(?=\[.+\])', anot)):
        parse_anot(device, x[0], method_of)
        # * duck.ai wrote this regex aswell
        args = regex.findall(r'\[(?:[^\[\]]+|(?R))*\]', anot)[0][1:-1]
        for i, arg in enumerate(args.split(','), 1):
            parse_anot(device, arg.strip(), method_of)
        device.app(f'imm {i}', 'tuple', 'anot')

def parse_anots(device, foo: function, method_of=None):
    sig = inspect.signature(foo, annotation_format=annotationlib.Format.STRING)
    params = dict(sig.parameters)
    for param in params:
        device.app(f"string '{'*' if str(params[param])[0]=='*' else ''}{param}'")
    device.app(f'imm {len(params)}', 'tuple')
    for i, param in enumerate(params.values()):
        if param.annotation is param.empty:
            if method_of and i == 0:
                device.app('hint Self')
            else:
                device.app('hint None')
        else:
            parse_anot(device, param.annotation, method_of)
    if params:
        parse_anot(device, sig.return_annotation, method_of)
        device.app(f'imm {i+2}', 'tuple')

def parse_funct(device, name: str, foo: function, method_of=None):
    for f in foo.__code__.co_consts:
        if isinstance(f, type(foo.__code__)):
            for g in f.co_names:
                if g not in __builtins__ and g not in device.deps and g in globals():
                    parse(device, g)
    parse_anots(device, foo, method_of)
    device.app('def')
    translate(device, name, foo, method_of)
    device.app('exit')
    if method_of is None:
        device.app(f'put {name}')

def parse_kern(device, name, foo: function, method_of=None):
    parse_anots(device, foo, method_of)
    device.app(f'kern {get_kern_name(foo)}')
    if method_of is None:
        device.app(f'put {name}')

def parse_class(device, name: str, foo: type):
    for i, meth in enumerate(filter(lambda x: isinstance(x, function), vars(foo).values())):
        device.app(f'string {meth.__name__!r}')
        parse(device, meth.__name__, meth, foo)
        device.app('imm 2', 'tuple')
    device.app(f'imm {i+1}', 'dict', f'class {name}')

def parse_const(device, name, foo: Any):
    if isinstance(foo, Screen):
        device.app('get Screen', 'call 0')
    elif isinstance(foo, Color):
        for arg in foo.args:
            device.app(f'imm {arg}')
        device.app('imm 3\nbuild tuple\nrgb')
    device.app(f'put {name}')


def parse_other(device, name: str, foo, method_of=None):
    if foo in get_kerns().values():
        parse_kern(device, name, foo, method_of)
    elif isinstance(foo, function):
        parse_funct(device, name, foo, method_of)
    elif isinstance(foo, type):
        parse_class(device, name, foo)
    else:
        parse_const(device, name, foo)

def parse_op(device, name, foo, method_of=None):
    parse_other(device, name, foo, method_of)
    device.app(f'op {get_op_name(foo)}')

def parse(device, name: str, foo=None, method_of=None):
    if foo is None:
        foo = globals()[name]
    if foo in get_ops().values():
        parse_op(device, name, foo, method_of)
    else:
        parse_other(device, name, foo, method_of)