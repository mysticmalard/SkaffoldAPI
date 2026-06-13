# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 MysticMalard

from ...fancyDecorator import _fancyDecorator

__all__ = ['_kerns', '_kern', '_ops', '_op']

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