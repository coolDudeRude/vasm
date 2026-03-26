from pprint import pprint
from typing import Optional
from importlib.resources import files
from argparse import ArgumentParser, Namespace

import xivasm


def parse_arguments(argument_string: Optional[str] = None) -> Namespace:
    """Parse commandline arguments."""
    arg_parser = ArgumentParser(description="Assembler for stackvm-xonotic")
    arg_parser.add_argument(
        "file", nargs="+", help="stackvm-xonotic program source file", metavar="file"
    )
    arg_parser.add_argument(
        "-o",
        "--output",
        dest="output",
        help="output filename of the assembled code",
        metavar="file",
        default="a.cfg",
    )
    arg_parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + xivasm.__version__
    )

    if argument_string is not None:
        return arg_parser.parse_args(argument_string)
    return arg_parser.parse_args()


def main():
    arguments = parse_arguments()

    # The file executed before anything else is preprocessed
    directives = files("xivasm") / "data/directives.m4"

    # First preprocess the file
    preprocessor = xivasm.M4(
        prefix_builtins=True,
        generate_syncline=True,
        process_before_syncline=[str(directives)],
    )
    preprocessor.add_argument("-Um4_syscmd")  # disable system program invocation.
    preprocessor.add_argument("-Um4_esyscmd")  # disable system program invocation.

    sources = []
    try:
        for file in arguments.file:
            sources.append(preprocessor.process_file(file))
    except FileNotFoundError as e:
        print("xivasm: " + str(e))
        return xivasm.exceptions.PREPROCESSOR_ERROR
    except RuntimeError as e:
        print("xivasm: " + str(e))
        return xivasm.exceptions.PREPROCESSOR_ERROR

    # Generate synline map
    source_maps = []
    for source in sources:
        source_maps.append(xivasm.source.create_synline_map(source))

    # Parses the processed text
    source_tokens = []
    try:
        for source, source_map, filename in zip(sources, source_maps, arguments.file):
            filename = filename.rpartition("/")[-1]
            source_tokens.append(xivasm.parser.parse(source, source_map, filename))
    except xivasm.exceptions.ParsingError as e:
        error_report = str(e)
        print(f"xivasm: {error_report}")
        return xivasm.exceptions.PARSING_ERROR

    units = []
    # Construct a translation unit
    try:
        for tokens, filename in zip(source_tokens, arguments.file):
            filename = filename.rpartition("/")[-1]
            module_name = filename.rpartition(".")[0]
            resolver = xivasm.Resolver(tokens, module_name)
            units.append(resolver.generate_unit())
    except xivasm.exceptions.ResolverError as e:
        print(f"xivasm: {str(e)}")
        return xivasm.exceptions.RESOLVER_ERROR

    # Now finally link it
    try:
        linker = xivasm.Linker(units)
        linker.generate_code()
        linker.write_to_file(arguments.output)
        print(f"xivasm: program written to '{arguments.output}'")
    except xivasm.exceptions.LinkingError as e:
        print(f"xivasm: {str(e)}")
        return xivasm.exceptions.LINKER_ERROR

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
