"""Parser frontend for xivasm"""

import parsy
from . import ir
from . import source
from .exceptions import ParsingError


Token = ir.Symbol | ir.Instruction
Tokens = list[Token]
Markers = list[ir.SourceMarker]

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
identifier = parsy.regex(r"[a-zA-Z_.][a-zA-Z_0-9.]*").map(ir.Symbol).desc("identifier")
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


opcode_without_arguments = {
    "pop",
    "dup",
    "dot",
    "exch",
    "add",
    "mul",
    "div",
    "sub",
    "min",
    "max",
    "pow",
    "mod",
    "iseq",
    "isne",
    "islt",
    "isle",
    "isgt",
    "isge",
    "ret",
    "hlt",
    "and",
    "or",
    "xor",
    "not",
    "bitand",
    "bitor",
    "bitxor",
    "bitnot",
    "neg",
    "sgn",
    "abs",
    "rand",
    "floor",
    "ceil",
    "exp",
    "log",
    "sin",
    "cos",
    "bound",
    "when",
    "union",
    "intersection",
    "difference",
    "shuffle",
    "fmt_localtime",
    "fmt_gmtime",
    "dp_time",
    "hash_md4",
    "hash_sha256",
    "crc16",
    "fmt_sprintf",
    "fexists",
    "assert_fexists",
    "eval",
    "store_vfs",
    "load_vfs",
    "call_vfs",
    "cstore_vfs",
    "cload_vfs",
}

arg_num = lexeme(hexadecimal | decimal | integer)
arg_id = lexeme(identifier)
arg_str = lexeme(string_literal)

arg_num_or_id = arg_num | arg_id

opcode_with_one_argument = {
    "push": arg_num_or_id,
    "jmp": arg_id,
    "jif": arg_id,
    "call": arg_id,
    "store_l": arg_id,
    "load_l": arg_id,
    "store_g": arg_id,
    "load_g": arg_id,
    "asis": arg_str,
    "cload": arg_id,
    "cstore": arg_id,
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


def add_metadata(
    index: int, tok: Token, text: str, source_map: Markers, filename: str
) -> Token:
    file, row, col = source.get_original_location(text, source_map, index)
    meta = ir.Metadata(row=row, column=col, file=file or filename)
    tok.metadata = meta
    return tok


def create_parser(text: str, source_map: Markers, filename: str) -> parsy.Parser:

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
            arg = opcode_with_one_argument.get(opcode_val)
            return with_meta(arg).map(
                lambda args: ir.Instruction(op=opcode_val, args=args)
            )

        if opcode_val in opcode_without_arguments:
            return parsy.success(ir.Instruction(op=opcode_val))

        return parsy.fail(f"Invalid opcode {opcode_val}")

    word = parsy.regex(r"[a-z_][a-z_0-9]+")
    opcode = lexeme(word).bind(get_instruction)
    instruction = with_meta(opcode.desc("opcode"))
    label = with_meta(lexeme(identifier.skip(colon).desc("label")))
    statement = label | instruction

    return ignored >> statement.many()


def parse(text: str, source_map: Markers, filename: str = "noname") -> Tokens:
    """Parses the input string and generates tokens"""
    program_parser = create_parser(text, source_map, filename)
    try:
        tokens = program_parser.parse(text)
        return tokens
    except parsy.ParseError as e:
        file, row, column = source.get_original_location(text, source_map, e.index)
        metadata = ir.Metadata(row, column, file)
        raise ParsingError(f"expected {', '.join(e.expected)}", metadata) from e
