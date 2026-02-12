import unittest
from vasm.assembler import Assembler, AssemblerError
from vasm.codegen import CodegenError
from vasm.parser import ParserError


class TestAssembler(unittest.TestCase):
    def test_assemble_program(self):
        ass = Assembler("tests/samples/factorial.s", output="a.cfg")
        expected = """alias vm.rom.0 "push 8"
alias vm.rom.1 "call 4"
alias vm.rom.2 "dot"
alias vm.rom.3 "hlt"
alias vm.rom.4 "store_l n"
alias vm.rom.5 "load_l n"
alias vm.rom.6 "push 1"
alias vm.rom.7 "islt"
alias vm.rom.8 "jif 16"
alias vm.rom.9 "load_l n"
alias vm.rom.10 "push 1"
alias vm.rom.11 "sub"
alias vm.rom.12 "call 4"
alias vm.rom.13 "load_l n"
alias vm.rom.14 "mul"
alias vm.rom.15 "ret"
alias vm.rom.16 "push 1"
alias vm.rom.17 "ret"
"""
        ass.assemble()
        self.assertEqual(ass.code, expected)

    def test_invalid_file_path(self):
        ass = Assembler(file="test.s", output="a.cfg")
        self.assertRaises(AssemblerError, ass.assemble)

    def test_parser_error(self):
        ass = Assembler(file="tests/samples/parser_error.s", output="a.cfg")
        self.assertRaises(ParserError, ass.assemble)

    def test_codegen_error(self):
        ass = Assembler(
            file="tests/samples/codegen_undefined_label_error.s", output="a.cfg"
        )
        self.assertRaises(CodegenError, ass.assemble)

        ass = Assembler(
            file="tests/samples/codegen_redefining_label_error.s", output="a.cfg"
        )
        self.assertRaises(CodegenError, ass.assemble)


if __name__ == "__main__":
    unittest.main()
