#!/usr/bin/env python

from tabulate import tabulate
from time import sleep


class Instr():

    def __init__(self, count):
        self._count = count

    def isExit(self):
        return False

    @property
    def count(self):
        return self._count

    def expand(self):
        expanded = [self.__class__(0)]

        for _ in range(self._count -1):
            expanded.append(self.__class__(0))

        return expanded


class CPU(Instr):

    def __repr__(self):
        if self._count:
            return "CPU({count})".format(count=self._count)
        else:
            return "CPU"


class IO(Instr):

    def __repr__(self):
        if self._count:
            return "IO({count})".format(count=self._count)
        else:
            return "IO"


class EXIT(Instr):

    def isExit(self):
        return True

    def __repr__(self):
        return "EXIT"


class Program():

    def __init__(self, name, instructions):
        self._name = name
        self._instructions = self.expand(instructions)

    @property
    def name(self):
        return self._name

    @property
    def instructions(self):
        return self._instructions

    def expand(self, instructions):
        expanded = []

        for instr in instructions:
            expanded.extend(instr.expand())

        if not expanded[-1].isExit():
            expanded.append(EXIT(0))

        return expanded

    def __repr__(self):
        return "Program({name}, {instructions})".format(name=self._name, instructions=self._instructions)


class Cpu():

    def __init__(self, mem):
        self._memory = mem
        self._pc = 0
#Guarda la ultima instruccion que se ejecuta (que no sea exit)
        self._ir = Instr(1)

    #Se elimina el while y se redefine de forma recursiva (not the best practice)
    def start(self):
        op = self._memory.fetch(self._pc)
        if not op.isExit():
            ir = op
            self._tick(op)
            self.start()

    @property
    def pc(self):
        return self._pc

    @pc.setter
    def pc(self, addr):
        self._pc = addr

    def _tick(self, op):
        print("Exec: {op}, PC={pc}".format(op=op, pc=self._pc))
        sleep(1)
        self._pc += 1

    def __repr__(self):
        return "CPU(PC={pc})".format(pc=self._pc)


class Memory():

    def __init__(self):
        self._memory = []

    def load(self, program):
        self._memory = program.instructions

    def fetch(self, addr):
        return self._memory[addr]

    def __repr__(self):
        return tabulate(enumerate(self._memory), tablefmt='psql')


class SO():

    def __init__(self):
        self._memory = Memory()
        self._cpu = Cpu(self._memory)
        self._cpus= []

    #Ejecuta una lista de programas, uno detras de otro
    def execAll(self, programs):
        for prog in programs:
            self.exec(prog)

    def exec(self, prog):
        self._memory.load(prog)
        print(self)
        self._cpu.pc = 0
        self._cpu.start()
        print(self._cpu._ir)

    def __repr__(self):
        return "{cpu}\n{mem}".format(cpu=self._cpu, mem=self._memory)


if __name__ == '__main__':
    p = Program("test.exe", [CPU(5), IO(2), CPU(3)])
    p1 = Program("test.exe", [IO(2), CPU(3)])
    p2 = Program("test.exe", [CPU(5), IO(2)])
    progs = [p, p1, p2]
    so = SO()
    so.execAll(progs)
