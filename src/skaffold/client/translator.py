# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 MysticMalard

import builtins

from .firmware import *

import dis, inspect, annotationlib, regex

# * dis._nb_ops enumerates possible values
# * this list shows what have been implimented
bin_op_decode = list(map(lambda x: x[1], dis._nb_ops))
# opmap_r = dict(map(lambda x: x[::-1], dis.opmap.items()))
known_func_attrs = ['closure']
known_intr1_calls = ['INTRINSIC_LIST_TO_TUPLE', 'INTRINSIC_STOPITERATION_ERROR']

def get_effect(inst):
    return dis.stack_effect(inst.opcode, inst.oparg)

# TODO
def translate(device, name: str, foo: function, method_of=None):
    if method_of:
        Self = method_of.__name__
    else:
        Self = name
    code = dis.Bytecode(foo)
    # ! FOR DEBUGGING
    # print(code.info())
    # print(code.dis())
    device.deb(code.info())
    device.deb(code.dis())
    insts = iter(code)
    def add_inst(*new_insts):
        nonlocal insts
        insts = iter(new_insts + tuple(insts))
    class Inst:
        def __init__(self, opname, **kwargs):
            nonlocal inst, oparg
            self.is_jump_target = inst.is_jump_target
            self.opname = opname
            self.opcode = dis.opmap[opname]
            self.argval = None
            self.oparg = oparg
            for key, item in kwargs.items():
                object.__setattr__(self, key, item)
    sig = inspect.signature(foo, annotation_format=annotationlib.Format.STRING)
    params = dict(sig.parameters).keys()
    for param in params:
        device.app(line := f'let {param}')
        # ! FOR DEBUGGING
        # print(line)
        # device.deb(line)
    next_label = 0
    stackptr = 0
    stackalerts = []
    stackalertfuncs = []
    labels = []
    try:
        while (inst := next(insts)):
            argval = inst.argval
            oparg = inst.oparg
            effect = dis.stack_effect(inst.opcode, inst.oparg)
            # if inst.is_jump_target:
            #    labels.append(f'L{(next_label := next_label + 1)}')
            match inst.opname:
                case 'RESUME':
                    # if argval&3:
                    #     raise NotImplementedError(
                    #             f'Client JIT -> Unsupported instruction pattern: instruction <{inst.opname!r}> with arg {inst.argrepr!r}'
                    #         )
                    line = 'nop'
                    # line = 'resume'
                case 'LOAD_FAST_BORROW_LOAD_FAST_BORROW':
                    for arg in argval[::-1]:
                        add_inst(Inst('LOAD_FAST_BORROW', argval=arg))
                    line = 'nop'
                case 'LOAD_FAST_BORROW':
                    line = f'push {argval} !'
                case 'STORE_ATTR':
                    line = f'string {argval!r}\nsetattr'
                case 'LOAD_SMALL_INT':
                    line = f'imm {argval}'
                case 'LOAD_CONST':
                    if argval is None:
                        line = f'push None'
                    else:
                        if isinstance(argval, type(translate.__code__)):
                            if argval.co_name == '<genexpr>':
                                pass
                            #     l = len(argval.co_varnames)
                            # else:
                            #     l = argval.co_argcount
                            l = argval.co_argcount
                            for v in argval.co_varnames[:l]:
                                device.app(f'string {v!r}')
                                # ! DEBUG
                                # print(f'string {v!r}')
                            device.app(f'imm {l}', 'tuple', 'lambda')
                            # ! DEBUG
                            # print(f'imm {l}', 'tuple', 'lambda')
                            for v in argval.co_varnames[:l]:
                                device.app(f'let {v}')
                                # print(f'let {v}')
                            add_inst(*list(dis.Bytecode(argval)))
                            # ! DEBUG
                            device.deb(dis.Bytecode(argval).info())
                            device.deb(dis.Bytecode(argval).dis())
                            line = 'nop'
                        elif isinstance(argval, (int, float)):
                            if isinstance(argval, bool):
                                line = f'imm {int(argval)}'
                            elif isinstance(argval, int) and argval in range(256):
                                line = f'imm {argval}'
                            else:
                                line = f'{type(argval).__name__} {argval}'
                        elif isinstance(argval, slice):
                            for arg in (argval.start, argval.stop, argval.step):
                                add_inst(Inst('LOAD_CONST', argval=arg))
                            add_inst(Inst('BUILD_TUPLE', argval=3))
                            line = 'nop'
                        elif isinstance(argval, tuple):
                            for arg in argval:
                                add_inst(Inst('LOAD_CONST', argval=arg))
                        else:
                            raise NotImplementedError(
                                f'Client JIT -> Unsupported instruction pattern: instruction <{inst.opname!r}> with arg {inst.argrepr!r}'
                            )
                case 'RETURN_VALUE':
                    line = 'return'
                case 'YIELD_VALUE':
                    line = 'yield'
                case 'RETURN_GENERATOR':
                    if (ninst := next(insts)).opname != 'POP_TOP':
                        effect += get_effect(ninst)
                    # else:
                    #     effect += get_effect(ninst)
                        line = 'nop'
                case 'LOAD_FAST_LOAD_FAST':
                    for arg in argval[::-1]:
                        add_inst(Inst('LOAD_FAST', argval=arg))
                    line = 'nop'
                case 'LOAD_FAST':
                    line = f'push {argval}'
                case 'LOAD_FAST_CHECK':
                    line = f'push {argval} c'
                case 'LOAD_GLOBAL':
                    line = f'get {argval}'
                    if (y := list(filter(lambda x: argval in x.__members__, enums))):
                        line = f'imm {int(y[0][argval])} e'
                    elif argval not in device.deps or argval in get_ops() or argval in get_kerns():
                        if argval in __builtins__:
                            if isinstance(__builtins__[argval], type):
                                line += ' >'
                            else:
                                line += ' g'
                        else:
                            line += ' #>'
                        stackalerts.append(stackptr+1)
                        stackalertfuncs.append(argval)
                case 'BINARY_OP':
                    if inst.argrepr in bin_op_decode:
                        line = f'bop {inst.argrepr}'
                    else:
                        raise NotImplementedError(
                            f'Client JIT -> Unsupported instruction pattern: instruction <{inst.opname!r}> with arg <{inst.argrepr!r}>'
                        )
                case 'COMPARE_OP':
                    line = f'bop {argval}'
                    if inst.arg&16:
                        line += ' b'
                case 'MAKE_FUNCTION':
                    line = 'exit'
                case 'LOAD_ATTR':
                    line = f'string {argval!r}\ngetattr'
                case 'CALL':
                    line = f'call {argval}'
                    if stackalerts and stackalerts[-1] == stackptr+effect:
                        stackalerts.pop()
                        line = f'{(s := stackalertfuncs.pop())} {argval} {'#' if s in get_ops() else '<'}'
                case 'PUSH_NULL':
                    line = 'nop'
                case 'CALL_FUNCTION_EX':
                    line = 'call *'
                    if stackalerts and stackalerts[-1] == stackptr+effect:
                        stackalerts.pop()
                        line = f'{stackalertfuncs.pop()} * #'
                case 'SET_FUNCTION_ATTRIBUTE':
                    if inst.argrepr in known_func_attrs:
                        line = 'nop'
                    else:
                        raise NotImplementedError(
                            f'Client JIT -> Unsupported instruction pattern: instruction <{inst.opname!r}> with arg <{inst.argrepr!r}>'
                        )
                case 'MAKE_CELL':
                    line = f'cell {argval}'
                case 'LOAD_DEREF':
                    line = f'nlcl {argval}'
                case 'COPY_FREE_VARS':
                    line = 'nop'
                case 'BUILD_TUPLE':
                    line = f'imm {argval}\ntuple'
                case 'BUILD_LIST':
                    line = f'imm {argval}\nlist'
                    if argval == 0:
                        line += ' %'
                case 'BUILD_SET':
                    line = f'imm {argval}\nset'
                case 'BUILD_SLICE':
                    line = f'slice'
                case 'BINARY_SLICE':
                    line = f'push None\nslice'
                case 'LIST_EXTEND':
                    line = 'bop +'
                case 'CALL_INTRINSIC_1':
                    if inst.argrepr in known_intr1_calls:
                        match inst.argrepr:
                            case 'INTRINSIC_LIST_TO_TUPLE':
                                line = 'cast tuple $'
                            case 'INTRINSIC_STOPITERATION_ERROR':
                                next(insts)
                                line = 'nop'
                    else:
                        raise NotImplementedError(
                            f'Client JIT -> Unsupported instruction pattern: instruction <{inst.opname!r}> with arg <{inst.argrepr!r}>'
                        )
                case 'STORE_SUBSCR':
                    line = 'store'
                case 'STORE_FAST':
                    line = f'let {argval}'
                case 'STORE_FAST_STORE_FAST':
                    for arg in argval[::-1]:
                        add_inst(Inst('STORE_FAST', argval=arg))
                    line = 'nop'
                case 'FOR_ITER':
                    line = f'for {inst.argrepr}'
                case 'POP_TOP':
                    line = 'nop'
                case 'JUMP_BACKWARD':
                    line = f'jump {inst.argrepr}'
                case 'JUMP_FORWARD':
                    line = f'jump {inst.argrepr}'
                case 'END_FOR':
                    line = 'pop f'
                case 'POP_ITER':
                    line = 'pop i'
                case 'GET_ITER':
                    line = 'iter'
                case 'UNPACK_SEQUENCE':
                    line = 'unpack'
                case 'DELETE_FAST':
                    line = f'del {argval}'
                case 'TO_BOOL':
                    line = 'cast bool'
                case 'POP_JUMP_IF_FALSE':
                    line = f'if {inst.argrepr}'
                case 'POP_JUMP_IF_TRUE':
                    add_inst(Inst('UNARY_NOT', argval=None), Inst('POP_JUMP_IF_FALSE', argrepr=inst.argrepr))
                    line = 'nop'
                case 'POP_JUMP_IF_NONE':
                    add_inst(Inst('PUSH_NULL'), Inst('IS_OP'))
                    line = 'nop'
                case 'IS_OP':
                    line = 'is'
                case 'CONTAINS_OP':
                    line = 'in'
                case 'UNARY_NOT':
                    line = 'not'
                case 'NOT_TAKEN':
                    line = 'nop'
                case 'COPY':
                    line = f'copy {argval}'
                case 'SWAP':
                    line = f'swap {argval}'
                case 'EXTENDED_ARG':
                    line = 'nop'
                case 'NOP':
                    line = 'nop'
                case _:
                    # ! NOT FOR DEBUGGING
                    # ! DO NOT REMOVE
                    raise NotImplementedError(
                        f'Client JIT -> Unsupported instruction: {inst.opname!r}'
                        )
            # if labels:
            #     line += f' {labels.pop()}'
            if inst.is_jump_target:
               line += f' L{(next_label := next_label + 1)}'
            stackptr += effect
            device.app((line := line.replace(f' {Self}', 'Self')))
            # ! FOR DEBUGGING
            # print(line)
    except StopIteration:
        pass
    # ! FOR DEBUGGING
    # print('exit\n\n')