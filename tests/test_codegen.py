import unittest
from vasm.parser import program_parser
from vasm.codegen import Codegen, CodegenError


class TestCodegen(unittest.TestCase):
    def test_codegen(self):
        program = """
_main:
    push 20
    call _square
    hlt

_square:
    dup
    mul
    ret
"""

        expected_result = """alias vm.rom.0 "push 20"
alias vm.rom.1 "call 3"
alias vm.rom.2 "hlt"
alias vm.rom.3 "dup"
alias vm.rom.4 "mul"
alias vm.rom.5 "ret"
"""
        symbol_table = {"_main": 0, "_square": 3}
        tokens = program_parser.parse(program)

        self.assertEqual(len(tokens), 8)
        cg = Codegen(tokens)
        code = cg.emit()
        self.assertEqual(cg.symbol_table, symbol_table)
        self.assertEqual(expected_result, code)

    def test_error_undefined_symbol(self):
        program = """
_init:
    call _main
    hlt
"""
        tokens = program_parser.parse(program)
        self.assertEqual(len(tokens), 3)
        cg = Codegen(tokens)
        self.assertRaises(CodegenError, cg.emit)

    def test_error_redefining_symbol(self):
        program = """
_init:
    push 20
    push 40
    mul

_init:
    hlt
"""
        tokens = program_parser.parse(program)
        self.assertEqual(len(tokens), 6)
        cg = Codegen(tokens)
        self.assertRaises(CodegenError, cg.emit)

    def test_asis_opcode(self):
        program = r"""
main:
    asis("rpn /VM_VERSION load \"Running Version %s\" dbpush dbpush")
    call sprintf
    dot
    hlt

sprintf:
    asis("rpn dbpop dbpop sprintf1s dbpush")
    ret
"""
        tokens = program_parser.parse(program)
        self.assertEqual(len(tokens), 8)
        cg = Codegen(tokens)
        expected = r"""alias vm.rom.0 "rpn /VM_VERSION load \"Running Version %s\" dbpush dbpush"
alias vm.rom.1 "call 4"
alias vm.rom.2 "dot"
alias vm.rom.3 "hlt"
alias vm.rom.4 "rpn dbpop dbpop sprintf1s dbpush"
alias vm.rom.5 "ret"
"""
        result = cg.emit()
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
