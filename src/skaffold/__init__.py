# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 MysticMalard

__version__ = '0.0.2'


from .client import *

def pattern(foo):
    return foo

class Client:
    def __init__(self):
        self.code = []
        self.asm = [f'ver {__version__}']
        self.deps = []
        self.pending = []
        self.decs = {}
        self.patterns = {}
        include(self, SCREEN)
        self.deps.append('SCREEN')
    def add_pattern(self, foo):
        include_funct(self, foo)
        self.patterns[foo.__name__] = foo
    def setup(self, *args):
        for arg in args:
            self.add_pattern(arg)
    def build(self):
        for job in self.deps:
            parse(self, job)
        for job in self.patterns.items():
            parse(self, *job)
    def app(self, *lines: tuple[str, ...]):
        for line in ('\n'.join(lines)).splitlines():
            self.asm.append(line)

def get_clients():
    pass

def get_macropad():
    return Client()