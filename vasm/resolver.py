"""Generator for Translation Unit"""

from . import ir
from .exceptions import ResolverError


class Resolver:
    BRANCH_INST = ("call", "jmp", "jif")

    def __init__(
        self, tokens: list[ir.Instruction | ir.Symbol], module_name: str = "noname"
    ) -> None:
        self.tokens = tokens

        self.unit = ir.TranslationUnit(name=module_name)
        self.local_definitions = set()
        self.current_address = 0

    def _extract_local_symbols(self, tokens: list[ir.Instruction | ir.Symbol]) -> set:
        """Extract symbols declared in the local file, from token stream"""
        local_defs = set()

        for token in tokens:
            if isinstance(token, ir.Symbol):
                local_defs.add(token.name)
        return local_defs

    def _resolve_symbol(self, token: ir.Symbol) -> None:
        label_name = token.name

        # If label is redefined raise an error.
        if label_name in self.unit.labels or label_name in self.unit.exports:
            raise ResolverError(f"symbol '{label_name}' redefined", token.metadata)

        # Labels starting with a dot (".") are local labels
        if label_name.startswith("."):
            self.unit.labels[label_name] = self.current_address

        # Otherwise they are global labels, we should mangle them.
        # Nothing fancy just prefix with module name
        else:
            mangled_name = f"{self.unit.name}.{label_name}"
            # NOTE: vlink will look at unit.labels for label lookup then global symbol table i.e unit.exports
            # Maybe add global to labels table, since they belong to the same file.
            self.unit.exports[mangled_name] = self.current_address

    def _resolve_instruction(self, token: ir.Instruction) -> None:
        opcode = token.op
        # Validate and mangle labels in branch instructions
        if opcode in self.BRANCH_INST:
            # FIXME: make the parser strict on taking identifiers as argument for branch instructions
            if isinstance(token.args, ir.Symbol):
                target = token.args.name

                if target.startswith("."):
                    # raise error if local label is not defined
                    if target not in self.local_definitions:
                        raise ResolverError(
                            f"branching to undefined label '{target}'",
                            token.args.metadata,
                        )

                # Global label mangle it
                elif target in self.local_definitions:
                    token.args.name = f"{self.unit.name}.{target}"

                # External Symbol, track it
                elif target not in self.unit.extern:
                    self.unit.extern.append(target)
        # Add the token to unit tokens list
        self.unit.instructions.append(token)
        self.current_address += 1

    def generate_unit(self) -> ir.TranslationUnit:
        """Generate symbol table, resolve exported symbols and external symbols"""
        self.local_definitions = self._extract_local_symbols(self.tokens)

        for token in self.tokens:
            if isinstance(token, ir.Symbol):
                self._resolve_symbol(token)

            elif isinstance(token, ir.Instruction):
                self._resolve_instruction(token)

        return self.unit
