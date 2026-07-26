# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 MysticMalard

import regex

# TODO
def splice_ops(device):
    pass
#'tuple' | 'dict' | 'set' | 'list' | 'slice'
classes = ['tuple', 'dict', 'set', 'list', 'slice', 'map', 'filter', 'zip', 'enumerate', 'range']
def optimize_minimal(device):
    for line in device.temp:
        terms = line.split(' ')
        if (labels := regex.findall(r'(?<!to) L\d+', line)):
            label = ' '.join(set(labels))
        else:
            label = ''
        op = terms[0]
        if len(terms)-1:
            arg = terms[1]
        match op:
            case op if op in classes:
                line = f'build {op}'
            case op if regex.findall(r'<(?!=)', line):
                line = f'imm {arg}\nbuild {op}'
            case 'get' if '#>' in line:
                line = 'nop'
            case 'get' if arg == 'isinstance':
                pass
            case 'get' if ' g' in line:
                line = 'nop'
            case 'build' if arg in ['len', 'iter', 'isinstance']:
                line = arg
            case op if '#' in line:
                if arg == '*':
                    line = op
                else:
                    line = f'imm {arg}\nbuild tuple\n{op}'
            case 'get' if '>' in line:
                if arg in classes:
                    line = 'nop'
                else:
                    line = f'hint {arg}'
            case 'get' if arg == 'Self':
                line = 'hint Self'
            case 'push' if arg == 'None':
                line = 'hint None'
            case 'push' if '@' in line:
                line = f'nlcl {arg}'
            case 'int':
                line = f'big {arg}'
            case 'float':
                line = f'dbl {arg}'
            case 'copy' if arg == '1':
                line = 'cpyt'
            case 'copy':
                line = f'copy {int(arg)-1}'
            case 'call':
                if arg == '*':
                    line = 'call'
                else:
                    line = f'imm {arg}\nbuild tuple\ncall'
            case 'resume':
                if label:
                    line = 'nop'
                else:
                    line = 'nop'
            case 'if':
                line = f'if\njump {regex.findall(r'to L\d+', line)[0]}'
            case 'for':
                line = f'cpyt\nnext\ncpyt\nhint stop\nist\nif\njump {regex.findall(r'to L\d+', line)[0]}'
        if label.lstrip() != arg:
            # regex.match(r'^.+', line)
            line = regex.subf(r'^.+', fr'{{0}}{label}', line)
        device.app(line)
        # device.app(line.replace('\n', f'{label}\n', label.lstrip() != arg))

def optimize(device, level):
    device.temp = device.asm[:]
    device.asm = []
    optimize_minimal(device)