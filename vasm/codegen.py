from .tokens import Label, Opcode


class CodegenError(Exception):
    pass


class Codegen:
    def __init__(self, tokens: list, text: str | None = None):
        self.tokens = tokens
        self.text = text
        self._address_counter = 0
        self._code = []
        self.symbol_table = {}

    def get_line(self, row):
        if self.text is None:
            return ""
        return self.text.split("\n")[row]

    def error(self, row, message, pointer_width=1):
        line_num = row
        line = self.get_line(line_num)
        row_info = " {row:>{padding}}|{line}".format(
            row=line_num + 1, padding=len(str(line_num + 1)), line=line
        )
        pointer = (" " * (len(row_info) - pointer_width)) + ("^" * pointer_width)
        line_info = f"{row_info}\n{pointer}"
        raise CodegenError(f"vasm: {message} @ {line_num + 1}\n{line_info}")

    def generate_symbol_table(self):
        self._address_counter = 0
        for token in self.tokens:
            start, token, _ = token
            if not isinstance(token, Label):
                if isinstance(token, Opcode):
                    self._address_counter += 1
                continue
            if token.name in self.symbol_table.keys():
                self.error(
                    start[0], f"redefining label '{token.name}'", len(token.name)
                )
            self.symbol_table[token.name] = self._address_counter

    def generate_code(self):
        self._address_counter = 0
        for token in self.tokens:
            start, token, _ = token
            if not isinstance(token, Opcode):
                continue
            opcode = token.opcode
            oprand = token.oprand
            if oprand is None:
                self._code.append(f"{opcode}")
            elif opcode in ("call", "jif", "jmp"):
                if oprand.value not in self.symbol_table.keys():
                    self.error(
                        start[0],
                        f"trying to access undefined label '{oprand.value}'",
                        len(oprand.value),
                    )
                addr = self.symbol_table[oprand.value]
                self._code.append(f"{opcode} {addr}")
            else:
                self._code.append(f"{opcode} {oprand.value}")

    def emit(self):
        self.generate_symbol_table()
        self.generate_code()
        text = ""
        for addr, code in enumerate(self._code):
            text += f'alias vm.rom.{addr} "{code}"\n'
        return text
