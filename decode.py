from pprint import pprint
from typing import List

"""For decoding pattern strings from user into iterable pattern 0bjects.

- Each pattern string is firstly split into PatternChunks, 
    optional ones surrounded by brackets `[]` and non-optional ones.
- Each PatternChunk is then further split into Pattern Atoms.
    LiteralAtoms are plain-text string to be printed,
    while ColumnNameAtom refers to specific cell of data rows to be extracted.
"""


# region Pattern atom
class PatternAtom:
    """The smallest unspiltable unit in a pattern."""

    def __init__(self) -> None:
        pass


class LiteralAtom(PatternAtom):
    """Pattern atom referring a plain-text string.

    The content of the atom will be directly printed out when generating
    formatted text.
    """

    def __init__(self, s: str, optional: bool = False) -> None:
        self.string = s

    def __repr__(self):
        return f'<{self.__class__.__name__}, "{self.string}">'


class ColumnNameAtom(PatternAtom):
    """Special pattern atom referring a column name.

    For each data row, the corresponding cell of the column will be extracted
    and filled into the generated text.
    """

    def __init__(self, colname: str, optional: bool = False) -> None:
        self.colnanme = colname

    def __repr__(self):
        return f'<{self.__class__.__name__}, "{self.colnanme}">'


# endregion


# region Pattern chunk
class PatternChunk:
    """A pattern chunk stores one or more pattern atoms in sequence.

    The pattern chunk is basically used for controlling the optional segments
    surrounded by bracket [] in pattern strings using its `is_optional()` method.

    Use `get_pattern_chunk()` and `get_optional_pattern_chunk()` to safely retrieve
    PatternChunk objects with validating (an optional chunk must contain at least
    one ColumnNameAtom).
    """

    def __init__(self, atoms: List[PatternAtom], optional: bool) -> None:
        self._atoms = atoms
        self._optional = optional

    def is_optional(self) -> bool:
        return self._optional

    def __repr__(self) -> str:
        s_atoms = ", ".join([str(atom) for atom in self._atoms])
        s = f"<PatternChunk: {s_atoms}, optional={self.is_optional()}>"
        return s

    def __iter__(self):
        """Iterate over all atoms in the chunk in sequence."""
        self._idx = 0
        return self

    def __next__(self):
        if self._idx >= len(self._atoms):
            raise StopIteration
        val = self._atoms[self._idx]
        self._idx += 1
        return val


def get_pattern_chunk(atoms: List[PatternAtom]):
    return PatternChunk(atoms, optional=False)


def get_optional_pattern_chunk(atoms: List[PatternAtom]):
    def contain_colname_atom(atoms):
        flg = False
        for atom in atoms:
            if isinstance(atom, ColumnNameAtom):
                flg = True
                break
        return flg

    if not contain_colname_atom(atoms):
        print(
            "Warning: Your optional pattern chunk contains no column name atom, "
            "fall back to normal non-optional chunk. "
            "Check your pattern string if it is not done on purpose."
        )
        return get_pattern_chunk(atoms)
    return PatternChunk(atoms, optional=True)


# endregion


Pattern = List[PatternChunk]


def validate_pattern_string(s: str) -> None:
    """Guarantee the given string is a valid pattern string."""

    def check_dollar(s):
        escape = False
        unpaired_dollar = False
        for c in s:
            if c == "$" and not escape:
                if unpaired_dollar:
                    unpaired_dollar = False
                else:
                    unpaired_dollar = True
            if c in "[]" and not escape and unpaired_dollar:
                raise ValueError('Invalid Pattern String: Brackets "[]" inside $$ key.')
        assert not unpaired_dollar, 'Invalid Pattern String: Dangling "$"'

    def check_bracket(s):
        escape = False
        previous_bracket = "]"
        for c in s:
            if c == "\\" and not escape:
                escape = True
                continue
            if c == "[" and not escape:
                assert previous_bracket != "[", 'Invalid Pattern String: Nested "["'
                previous_bracket = c
            elif c == "]" and not escape:
                assert previous_bracket == "[", 'Invalid Pattern String: Dangling "["'
                previous_bracket = c
            escape = False
        assert previous_bracket != "[", 'Invalid Pattern String: Dangling "["'

    check_dollar(s)
    check_bracket(s)


def decode_pattern_string(pattern_string: str) -> Pattern:
    """Break down the given pattern string into a list of pattern chunks for iterating through."""

    validate_pattern_string(pattern_string)

    pattern = []
    curr_string = ""
    curr_atoms = []
    in_colname_atom = False
    in_optional_chunk = False
    escape = False
    for c in pattern_string:
        if c == "\\" and not escape:
            escape = True
            continue
        elif c == "$" and not escape:
            if not in_colname_atom:
                if curr_string != "":
                    curr_atoms.append(LiteralAtom(curr_string))
                    curr_string = ""
                in_colname_atom = True
            else:
                if curr_string != "":
                    curr_atoms.append(ColumnNameAtom(curr_string))
                    curr_string = ""
                in_colname_atom = False
        elif c == "[" and not escape:
            if curr_string != "":
                curr_atoms.append(LiteralAtom(curr_string))
                curr_string = ""
            if curr_atoms != []:
                pattern.append(get_pattern_chunk(curr_atoms))
                curr_atoms = []
            in_optional_chunk = True
        elif c == "]" and not escape:
            if curr_string != "":
                curr_atoms.append(LiteralAtom(curr_string))
                curr_string = ""
            if curr_atoms != []:
                pattern.append(get_optional_pattern_chunk(curr_atoms))
                curr_atoms = []
            in_optional_chunk = False
        else:
            curr_string += c
            escape = False
    if curr_string != "":
        curr_atoms.append(LiteralAtom(curr_string))
    if curr_atoms != []:
        pattern.append(get_pattern_chunk(curr_atoms))
    return pattern


if __name__ == "__main__":
    s = "$颁发时间$, $项目$[/$奖项$], $机构$[/$级别$]"
    decode = decode_pattern_string(s)
    pprint(decode)
