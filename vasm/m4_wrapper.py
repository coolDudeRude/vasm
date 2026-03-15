"""GNU m4 wrapper for vasm preprocessor frontend"""

import shutil
import pathlib
import subprocess


class M4:
    """GNU m4 wrapper class"""

    def __init__(
        self,
        prefix_builtins: bool = False,  # prefix m4 builtin commands with "m4_"
        generate_syncline: bool = False,  # Generate line markers like '#line 1 "main.s"'
        process_before_syncline: list[str] | None = None,
    ) -> None:
        self._prefix_builtins = prefix_builtins
        self._generate_syncline = generate_syncline
        self._process_before_syncline = process_before_syncline

        if not shutil.which("m4"):
            raise FileNotFoundError("Could not find m4 in PATH")

        self._arguments = ["m4"]

        if self._prefix_builtins:
            self._arguments.append("-P")

        if self._generate_syncline:
            if self._process_before_syncline is not None:
                self._check_file_path(self._process_before_syncline)
                self._arguments.extend(self._process_before_syncline)
            self._arguments.append("-s")

    def add_argument(self, argument: str) -> None:
        """Add argument to the default arguments list"""
        self._arguments.append(argument)

    def _check_file_path(self, files: list[str]) -> None:
        for file in files:
            path = pathlib.Path(file)
            if not path.is_file():
                raise FileNotFoundError(f"'{file}' no such file exists.")

    def _build_args(self, macros: dict | None, includes: list[str] | None) -> list:
        args = []

        if includes:
            for path in includes:
                args.append(f"-I{path}")

        if macros:
            for key, value in macros.items():
                args.append(f"-D{key}={value}")

        return args

    def _run(self, arguments: list[str], input_string: str | None = None) -> str:
        """Executes the m4 binary with passed arguments, if input_string is provided,
        m4 will read from stdin and process the string"""

        if input_string is not None and arguments[-1] != "-":
            arguments.append("-")

        try:
            result = subprocess.run(
                self._arguments + arguments,
                input=input_string,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"preprocessor encountered, see the log below\n {e.stderr.strip()}"
            ) from e

    def get_version(self) -> str:
        """Get the version of GNU m4 installed"""
        version_info = self._run(["--version"]).strip()
        version = version_info.split("\n")[0].rpartition(" ")[-1]
        return version

    def process_string(
        self, string: str, macros: dict | None = None, includes: list[str] | None = None
    ) -> str:
        """Process string literal with GNU m4"""
        arguments = self._build_args(macros, includes)
        return self._run(arguments, string)

    def process_file(
        self, file: str, macros: dict | None = None, includes: list[str] | None = None
    ) -> str:
        """Process file with GNU m4"""
        self._check_file_path([file])
        arguments = self._build_args(macros, includes)
        return self._run(arguments + [file])
