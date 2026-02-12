import unittest
from vasm.parser import Parser, ParserError


class TestParser(unittest.TestCase):
    def test_syntax(self):
        text = """_main:
            push 20
            pop
            dup
            dot
            add
            sub
            mul
            div
            pow
            min
            max
            load x
            gload y
            store x
            gstore y
            call _exit
            jmp _loop
            jif _target
            ret
            hlt
            eq
            ne
            lt
            le
            gt
            ge
        """
        tokens = Parser(text).parse()
        self.assertEqual(len(tokens), 27)

    def test_parser_error(self):
        self.assertRaises(ParserError, Parser("_main").parse)
        self.assertRaises(ParserError, Parser("push x").parse)
        self.assertRaises(ParserError, Parser("call 200").parse)


if __name__ == "__main__":
    unittest.main()
