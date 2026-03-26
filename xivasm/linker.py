"""Linker for xivasm"""

from . import ir
from .exceptions import LinkingError


class Linker:
    BRANCH_INST = ("call", "jmp", "jif")

    def __init__(self, units: list[ir.TranslationUnit]) -> None:
        self.units = units

        self.symbol_table: dict[str, int] = {}
        self.code = []
        self.current_unit = ir.TranslationUnit("none")

    def _get_label_address(self, token: ir.Symbol) -> int:
        name = token.name
        if (addr := self.current_unit.labels.get(name)) is not None:
            return addr
        if (addr := self.current_unit.exports.get(name)) is not None:
            return addr
        if (addr := self.symbol_table.get(name)) is not None:
            return addr
        raise LinkingError(f"Unresolved symbol '{token.name}'", token.metadata)

    def generate_code(self):
        # calculate base offset and populate symbol_table
        base_offset = 0
        for unit in self.units:
            unit.base_offset = base_offset
            for symbol in unit.labels:
                unit.labels[symbol] += base_offset

            for symbol in unit.exports:
                unit.exports[symbol] += base_offset
            self.symbol_table = {**self.symbol_table, **unit.exports}

            base_offset += len(unit.instructions)

        # Resolve labels and emit code
        for unit in self.units:
            self.current_unit = unit
            for instruction in unit.instructions:
                op = instruction.op
                arg = instruction.args
                if op in self.BRANCH_INST:
                    target_address = self._get_label_address(arg)
                    code = f"{op} {target_address}"
                elif isinstance(arg, ir.Symbol):
                    code = f"{op} {arg.name}"
                else:
                    code = f"{op} {arg}" if arg else op

                self.code.append(code)

    def write_to_file(self, file: str) -> None:
        with open(file, "w", encoding="utf-8") as output:
            program = ""
            for index, code in enumerate(self.code):
                program += f'alias vm.rom.{index} "{code}"\n'
            output.write(program)
