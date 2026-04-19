# StackVM Xonotic Assembler

An assembler for [stackvm-xonotic](https://github.com/coolDudeRude/stackvm-xonotic).

## Features

The assembler is quite primitive, but here are some important features:

- Preprocessor (using GNU m4)
- Global & Local Labels (local labels start with a period `"."`)
- File-scoped Labels (Global labels are automatically prefixed with source filename aka primitive namespaces)
- `asis` command to put string as instruction. (see [sprintf.s](/examples/sprintf.s))

## Installation

```
git clone https://github.com/coolDudeRude/xivasm
cd xivasm
python -m venv .venv
source .venv/bin/activate
pip install .
```

## Hacking

For modifying source code and testing changes, install `xivasm` using:

```
pip install --editable .
```

## Issues

### Parser

The parser is slow & difficult to debug. It's written using parsy. Might move to Lark.

### Object Files

The Assembler doesn't emit object files, so can't link separate source files with the linker. Will have to
assemble all the files at once. Like:

```
xivasm init.s main.s math.s ... -o prog.cfg
```

### Xonotic Script Buffer Limitation

Loading scripts exceeding `655,360` bytes will truncate the script. (TODO) Will have to split the script into chunks,
along with creating a main loader script that loads all the chunks.
Something like this:

```
prog.cfg
├── chunk.0.cfg
├── ...
└── chunk.n.cfg
```
