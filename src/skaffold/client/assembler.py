# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 MysticMalard

from pathlib import Path
import dis, struct, regex

def make_enum_dict(l) -> dict:
    return dict(map(lambda x: x[::-1], enumerate(l)))

path = Path(__file__).parent / "skaffold.arc"
with path.open() as f:
    insts, types, bops, kerns = f.read().split('$\n')
insts = make_enum_dict(insts.splitlines())
types = make_enum_dict(types.splitlines())
bops = make_enum_dict(bops.splitlines())
kerns = make_enum_dict(kerns.splitlines())

def double_to_hex(f):
    return struct.pack('<d', f)

def big_int_to_hex(n):
    return struct.pack('<q', n)

def uint16_t_to_hex(n):
    return struct.pack('<H', n)

def get_num(d, k):
    if k in d:
        return d[k]
    for i in range(len(d)+1):
        if i not in d.values():
            d[k] = i
            return i

def type_num(d, k):
    return get_num(d, k.lower())

def assemble(device):
    def addref(label):
        nonlocal labelrefs
        if label in labelrefs:
            labelrefs[label].append(len(device.code))
        else:
            labelrefs[label] = [len(device.code)]
    def splicerefs():
        nonlocal labelrefs, labels
        for label, refs in labelrefs.items():
            if label in labels:
                for ref in refs:
                    device.code[ref], device.code[ref+1] = labels[label]
    labels = {}
    labelrefs = {}
    local_types = types
    vars = {}
    globs = {'return':0, 'SCREEN':1, 'isinstance':2}
    ops = {}
    cells = {}
    scopestack = []
    for lineno, line in enumerate(device.asm):
        terms = line.split(' ')
        op = terms[0]
        if len(terms)-1:
            arg = terms[1]
        else:
            arg = None
        if op in insts:
            device.adi(insts[op])
        elif op in ops:
            device.adi(ops[op])
        match op:
            case 'exit':
                scope = scopestack.pop()
                for datum in uint16_t_to_hex(len(device.code)+2)[::-1]:
                    device.code.insert(scope[0], datum)
                vars = scope[1].copy()
                cells = scope[2].copy()
                labels = scope[3].copy()
                labelrefs = scope[4].copy()
            case 'ver':
                for i in arg.split('.')[::-1]:
                    device.adi(int(i))
            case 'imm':
                device.adi(int(arg))
            case 'push':
                device.adi(vars[arg])
            case 'put':
                device.adi(get_num(globs, arg))
            case 'let':
                device.adi(get_num(vars, arg))
            case 'get':
                device.adi(globs[arg])
            case 'cell':
                device.adi(get_num(cells, arg))
            case 'nlcl':
                device.adi(cells[arg])
            case 'poke':
                device.adi(cells[arg])
            case 'string':
                device.adi(*arg[1:-1], 0)
            case 'jump':
                if (o := regex.findall(r'(?<=to )L\d+', line)[0]) in labels:
                    device.adi(*labels[o])
                else:
                    addref(o)
                    device.adi(o, o)
            case 'def':
                scopestack.append((len(device.code), vars.copy(), cells.copy(), labels.copy(), labelrefs.copy()))
                vars.clear()
                labels.clear()
                labelrefs.clear()
            case 'lambda':
                scopestack.append((len(device.code), vars.copy(), cells.copy(), labels.copy(), labelrefs.copy()))
                vars.clear()
                labels.clear()
                labelrefs.clear()
            case 'class':
                device.adi(get_num(local_types, arg))
                get_num(globs, arg)
            case 'kern':
                device.adi(kerns[arg])
            case 'op':
                device.adi(get_num(ops, arg))
            case 'hint':
                device.adi(type_num(local_types, arg))
            case 'build':
                device.adi(type_num(local_types, arg))
            case 'cast':
                device.adi(type_num(local_types, arg))
            case 'bop':
                if arg in dict(dis._nb_ops).values() and '=' in arg:
                    device.adi(bops[arg[:-1]]|0x80)
                else:
                    device.adi(bops[arg])
            case 'copy':
                device.adi(int(arg))
            case 'swap':
                device.adi(int(arg))
            case 'big':
                device.adi(*big_int_to_hex(int(arg)))
            case 'dbl':
                device.adi(*double_to_hex(float(arg)))
        if (label := regex.findall(r'(?<!to )L\d+', line)):
            labels[label[0]] = uint16_t_to_hex(len(device.code))
            if label[0] in labelrefs:
                splicerefs()
    if (e := list(filter(lambda x: regex.Regex(r'(?<!to )L\d+').match(str(x)), device.code))):
        print(e)
    # print(device.code.index('L1'))
    return None