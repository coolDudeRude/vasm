from . import ir


PREPROCESSOR_ERROR = 1
PARSING_ERROR = 2
RESOLVER_ERROR = 3
LINKER_ERROR = 4


class AssemblerError(Exception):
    def __init__(self, message: str, metadata: ir.Metadata | None) -> None:
        super().__init__(message)
        self.message = message
        self.metadata = metadata if metadata else ir.Metadata(0, 0, "<no-metadata>")

    def __str__(self) -> str:
        return f"{self.message} at {self.metadata}"

    def get_detailed_report(self, source_code: str) -> str:
        """Generates a visual error report with a caret ^ pointing to the column."""
        lines = source_code.splitlines()
        error_line = (
            lines[self.metadata.row - 1] if self.metadata.row <= len(lines) else ""
        )

        # Build a visual pointer:
        # line text
        #      ^
        pointer = " " * self.metadata.column + "^"

        return f"{self}\n{error_line}\n{pointer}"


class ParsingError(AssemblerError):
    pass


class ResolverError(AssemblerError):
    pass


class LinkingError(AssemblerError):
    pass
