#!/usr/bin/env python

from tabulate import tabulate
from time import sleep
import unittest


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

    #tickea a mano
    def start(self):
        op = self._memory.fetch(self._pc)
        self._tick(op)


    @property
    def pc(self):
        return self._pc

    @pc.setter
    def pc(self, addr):
        self._pc = addr

    
    def _tick(self, op):
        print("Exec: {op}, PC={pc}".format(op=op, pc=self._pc))
        sleep(1)
        if not op.isExit():
            self._ir = op
        self._pc += 1

    def __repr__(self):
        return "CPU(PC={pc})".format(pc=self._pc)


class Memory():

    def __init__(self):
        self._memory = []

    def load(self, program):
        self._memory.extend(program.instructions)

    def fetch(self, addr):
        return self._memory[addr]

    def __repr__(self):
        return tabulate(enumerate(self._memory), tablefmt='psql')


class SO():

    def __init__(self):
        self._memory = Memory()
        self._cpu = Cpu(self._memory)

    #Tiene que Hacer el load del programa
    def exec(self, prog):
        self._memory.load(prog)

    def __repr__(self):
        return "{cpu}\n{mem}".format(cpu=self._cpu, mem=self._memory)


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.prog1 = Program("test.exe", [CPU(5), IO(2), CPU(3)])
        self.prog2 = Program("test.exe", [IO(2), CPU(3)])
        self.so = SO()

    def tearDown(self):
        self.so = SO()

    def test_cargar_un_programa(self):
        self.so.exec(self.prog1)
        self.assertTrue(len(self.so._memory._memory) == len(self.prog1.instructions))

    def test_cargar_dos_programas(self):
        self.so.exec(self.prog1)
        self.so.exec(self.prog2)
        expected = len(self.prog1.instructions) + len(self.prog2.instructions)
        self.assertEqual(len(self.so._memory._memory), expected)

    def test_ejecutar_primera_instruccion(self):
        self.so.exec(self.prog1)

        self.so._cpu.start

        expectedPC = 1
        expectedValorDeIR = "CPU"

        self.so._cpu.start()

        self.assertEqual(self.so._cpu.pc, expectedPC)
        self.assertEqual(repr(self.so._cpu._ir), "CPU")

    def test_al_ejecutar_un_exit_no_lo_guarda_en_ir(self):
        self.so.exec(self.prog1)
        self.so.exec(self.prog2)

        self.so._cpu.pc = 9
        self.so._cpu.start()

        expectedPC = 10
        expectedValorDeIR = "CPU"

        self.assertEqual(self.so._cpu.pc, expectedPC)
        self.assertEqual(repr(self.so._cpu._ir), "CPU")

        self.so._cpu.start()

        expectedPC = 11

        self.assertEqual (self.so._cpu.pc, expectedPC)
        self.assertEqual (repr(self.so._cpu._ir), "CPU")

if __name__ == '__main__':
    unittest.main()