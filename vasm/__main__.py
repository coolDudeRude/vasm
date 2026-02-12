from argparse import ArgumentParser
from .assembler import Assembler
from .__version__ import __version__


def main():
    argument_parser = ArgumentParser(description="Assembler for stackvm-xonotic")
    argument_parser.add_argument(
        "file", help="stackvm-xonotic program source file", metavar="file"
    )
    argument_parser.add_argument(
        "-o",
        dest="output",
        default="a.cfg",
        help="filename for assembled program (default: a.cfg)",
        metavar="output",
    )
    argument_parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + __version__
    )
    arguments = argument_parser.parse_args()

    ass = Assembler(file=arguments.file, output=arguments.output)

    try:
        ass.assemble()
        ass.write()
    except Exception as e:
        print(e.args[0])
        return 1
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
