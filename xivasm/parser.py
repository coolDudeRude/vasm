"""Parser frontend for xivasm"""

import parsy
from . import ir
from . import source
from .exceptions import ParsingError


## Parser Logic

# Ignore comments, whitespace and synline markers.
ignored = (
    (
        (parsy.string(";").desc("comment") | parsy.string("#").desc("directive"))
        >> parsy.regex(r"[^\n]*")
    )
    | parsy.whitespace.desc("whitespace")
).many()


## Primitives
identifier = parsy.regex(r"[a-zA-Z_.][a-zA-Z_0-9.]*").desc("identifier")
string_literal = (
    parsy.regex(r'"(.*)?"').map(lambda r: ir.String(r[1:-1])).desc("string")
)
integer = parsy.regex(r"[-]?[0-9]+").map(lambda i: ir.Number(int(i))).desc("integer")
decimal = (
    parsy.regex(r"[-]?[0-9]+[.][0-9]+").map(lambda f: ir.Number(float(f))).desc("float")
)
hexadecimal = (
    parsy.regex(r"0x[0-9a-fA-F]+").map(lambda r: ir.Number(int(r, 16))).desc("hex")
)

colon = parsy.string(":")


def lexeme(p: parsy.Parser) -> parsy.Parser:
    """Generates a parser that parses the desired elements while ignoring comments,
    and synline markers"""
    return p.skip(ignored)


def keyword(string: str) -> parsy.Parser:
    """Generates parser that parses literal words"""
    return parsy.regex(string + r"\b").desc(string)


argument = lexeme(decimal | integer | hexadecimal | identifier.map(ir.Symbol))

opcode_without_arguments = {
    "pop",
    "dup",
    "dot",
    "add",
    "mul",
    "div",
    "sub",
    "min",
    "max",
    "iseq",
    "isne",
    "islt",
    "isle",
    "isgt",
    "isge",
    "ret",
    "hlt",
}

opcode_with_one_argument = {
    "push",
    "jmp",
    "jif",
    "call",
    "store_l",
    "load_l",
    "store_g",
    "load_g",
}


opcode_mapping = {
    "load": "load_l",
    "store": "store_l",
    "gload": "load_g",
    "gstore": "store_g",
    "eq": "iseq",
    "ne": "isne",
    "lt": "islt",
    "le": "isle",
    "gt": "isgt",
    "ge": "isge",
    "psh": "push",
    "goto": "jmp",
}

token = ir.Symbol | ir.Instruction
markers = list[ir.SourceMarker]


def add_metadata(
    index: int, tok: token, text: str, source_map: markers, filename: str
) -> token:
    file, row, col = source.get_original_location(text, source_map, index)

    meta = ir.Metadata(row=row, column=col, file=file or filename)
    tok.metadata = meta
    return tok


def create_parser(
    text: str, source_map: list[ir.SourceMarker], filename: str
) -> parsy.Parser:

    def with_meta(p: parsy.Parser) -> parsy.Parser:
        return parsy.seq(parsy.index, p).map(
            lambda data: add_metadata(
                data[0],
                data[1],
                text,
                source_map,
                filename,
            )
        )

    def get_instruction(text: str):
        """Parse instruction and resolve it's alias mapping"""
        opcode_val = opcode_mapping.get(text, text)

        if opcode_val in opcode_with_one_argument:
            return with_meta(argument).map(
                lambda args: ir.Instruction(op=opcode_val, args=args)
            )

        if opcode_val in opcode_without_arguments:
            return parsy.success(ir.Instruction(op=opcode_val))

        return parsy.fail(f"Invalid opcode {opcode_val}")

    word = parsy.regex(r"[a-z_]+")

    opcode = lexeme(word).bind(get_instruction)

    instruction = with_meta(opcode.desc("opcode"))

    label = with_meta(lexeme(identifier.skip(colon).map(ir.Symbol).desc("label")))

    statement = label | instruction

    return ignored >> statement.many()


def parse(
    text: str, source_map: list[ir.SourceMarker], filename: str = "noname"
) -> list:
    """Parses the input string and generates tokens"""
    program_parser = create_parser(text, source_map, filename)
    try:
        tokens = program_parser.parse(text)
        return tokens
    except parsy.ParseError as e:
        file, row, column = source.get_original_location(text, source_map, e.index)
        metadata = ir.Metadata(row, column, file)
        raise ParsingError(f"expected {', '.join(e.expected)}", metadata) from e
