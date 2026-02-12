from pathlib import Path
from .parser import Parser
from .codegen import Codegen


class AssemblerError(Exception):
    pass


class Assembler:
    def __init__(self, file: str, output: str):
        self.file = file
        self.output = output
        self._code = ""

    @property
    def code(self):
        return self._code

    def path_exists(self, path: str):
        if Path(path).exists():
            return True
        return False

    def assemble(self):
        if not self.path_exists(self.file):
            raise AssemblerError(f"{self.file} no such file exists.")

        with open(self.file, "r") as infile:
            text = infile.read()

        parser = Parser(text)
        tokens = parser.parse()

        cg = Codegen(tokens, text)
        self._code = cg.emit()

    def write(self):
        with open(self.output, "w") as outfile:
            outfile.write(self._code)
