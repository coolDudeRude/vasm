from parsy import Parser, regex, seq, string, ParseError
from .tokens import Label, Opcode, Integer, Float, Ident, String


def literal(word: str) -> Parser:
    """Parser that only matches words that have line break.
    For example:

    call = literal("call")  # This will only parse "call" not the "call"
                            # in "calling". While parsy.string will match
                            # both, "call" and "call" in "calling", leaving
                            # behind "ing", which will result in parser error.
    """
    return regex(word + r"\b").desc(word)


# Primitives
req_whitespace = regex(r"\s+").desc("whitespace")
opt_whitespace = regex(r"\s*").desc("whitespace")

ident = regex("[A-Za-z_][A-Za-z_0-9]*").desc("identifier").map(Ident)
colon = string(":")

# literals
whole_number = regex("[0-9]+").desc("integer").map(Integer)
fractional_number = regex("[0-9]+[.][0-9]+").desc("float").map(Float)
number = fractional_number | whole_number

# String literal
string_lit = regex(r'"(.*)?"').desc("string literal").map(lambda r: String(r[1:-1]))

# boolean
true = literal("true").result(1).map(Integer)
false = literal("false").result(0).map(Integer)
boolean = true | false


label = (ident.map(lambda r: r.value) << colon).map(Label)

stack_op = (
    seq(literal("push") << req_whitespace, number | boolean)
    | literal("pop")
    | literal("dup")
    | literal("dot")
)

arithemtic_op = (
    literal("add")
    | literal("sub")
    | literal("mul")
    | literal("div")
    | literal("pow")
    | literal("min")
    | literal("max")
)

branch_op = seq(
    (literal("jmp") | literal("jif") | literal("call")) << req_whitespace, ident
) | literal("ret")

logical_op = (
    literal("eq").result("iseq")
    | literal("ne").result("isne")
    | literal("lt").result("islt")
    | literal("le").result("isle")
    | literal("gt").result("isgt")
    | literal("ge").result("isge")
)

io_op = seq(
    (
        literal("store").result("store_l")
        | literal("load").result("load_l")
        | literal("gstore").result("store_g")
        | literal("gload").result("load_g")
    )
    << req_whitespace,
    ident,
)

misc = literal("hlt")

asis = seq(
    literal("asis") << opt_whitespace << string("(") << opt_whitespace,
    string_lit << opt_whitespace << string(")"),
)


def map_opcode(result):
    if isinstance(result, list):
        return Opcode(result[0], result[1])
    return Opcode(result)


opcode = (
    stack_op
    | arithemtic_op
    | logical_op
    | branch_op
    | arithemtic_op
    | io_op
    | misc
    | asis
).map(map_opcode)

statement = opt_whitespace >> (label | opcode) << opt_whitespace
program_parser = statement.mark().many()


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, text):
        self.text = text

    def get_line_info(self, end=int):
        lines = self.text[:end].split("\n")
        line_num = len(lines)
        line = lines[-1]
        line_info = " {row:>{padding}}|{line}".format(
            row=line_num, padding=len(str(line_num)), line=line
        )
        pointer = (" " * len(line_info)) + "^"
        return line_num, f"{line_info}\n{pointer}"

    def parse(self):
        try:
            tokens = program_parser.parse(self.text)
        except ParseError as e:
            end = e.args[2]
            line_num, line_info = self.get_line_info(end)
            expected = ",".join(map(lambda r: f"'{r}'", e.args[0]))
            raise ParserError(f"vasm: expected {expected} at {line_num}\n{line_info}")

        return tokens
