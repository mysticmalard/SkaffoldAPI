# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 MysticMalard

from ...fancyDecorator import _fancyDecorator


_kerns = {}
@_fancyDecorator
def _kern(name: str, foo: function | type):
    _kerns[name] = foo
    return foo

_ops = {}
@_fancyDecorator
def _op(name: str, foo: function | type):
    _ops[name] = foo
    return foo

def get_ops():
    return _ops

def get_op_name(v: function | type) -> str:
    _rev_ops = {v: k for k, v in _ops.items()}
    return _rev_ops[v]

def get_kerns():
    return _kerns

def get_kern_name(v: function | type) -> str:
    _rev_kerns = {v: k for k, v in _kerns.items()}
    return _rev_kerns[v]

__all__ = ['_kern', '_op', 'get_ops', 'get_kerns', 'get_op_name', 'get_kern_name']