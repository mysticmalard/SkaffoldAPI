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
        self.temp = []
        self.deps = []
        self.pending = []
        self.raw = []
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
            # if line == 'imm True':
            # if 'get bisect' in line:
                # pass
            self.asm.append(line)
    def adi(self, *data):
        # * Yeah I just used the word "datum" in 2026
        # * Deal with it
        for datum in data:
            if isinstance(datum, str) and not len(datum)-1:
                datum = ord(datum)
            self.code.append(datum)
    def optimize(self, level=0):
        optimize(self, level)
    def assemble(self):
        assemble(self)
        self.code = bytes(self.code)
    def deb(self, *lines):
        for line in ('\n'.join(lines)).splitlines():
            self.raw.append(line)

def get_clients():
    pass

def get_macropad():
    return Client()