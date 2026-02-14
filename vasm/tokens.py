class Label:
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return f"Label({self.name})"

    def __repr__(self) -> str:
        return self.__str__()


class Ident:
    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return f"Ident({self.value})"

    def __repr__(self) -> str:
        return self.__str__()


class Integer:
    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return f"Integer({self.value})"

    def __repr__(self) -> str:
        return self.__str__()


class Float:
    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return f"Float({self.value})"

    def __repr__(self) -> str:
        return self.__str__()


class String:
    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return f"String({self.value})"

    def __repr__(self) -> str:
        return self.__str__()


class Opcode:
    def __init__(self, opcode: str, oprand=None) -> None:
        self.opcode = opcode
        self.oprand = oprand

    def __str__(self) -> str:
        if self.oprand is None:
            return f"Opcode({self.opcode})"
        return f"Opcode({self.opcode}, {self.oprand})"

    def __repr__(self) -> str:
        return self.__str__()
