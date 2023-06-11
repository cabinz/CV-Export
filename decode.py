from pprint import pprint
from typing import List

class PatternAtom:
    def __init__(self) -> None:
        pass

class ColumnNameAtom(PatternAtom):
    def __init__(self, colname: str, optional: bool=False) -> None:
        self.colnanme = colname
    
    def __repr__(self):
        return f'<{self.__class__.__name__}, "{self.colnanme}">'

class LiteralAtom(PatternAtom):
    def __init__(self, s: str, optional: bool=False) -> None:
        self.string = s
        
    def __repr__(self):
        return f'<{self.__class__.__name__}, "{self.string}">'
        
class PatternChunk:
    def __init__(self, atoms: List[PatternAtom], optional: bool) -> None:
        self._atoms = atoms
        self._optional = optional
        
    def is_optional(self) -> bool:
        return self._optional
    
    def __repr__(self) -> str:
        s_atoms = ', '.join([str(atom) for atom in self._atoms])
        s = f'<PatternChunk: {s_atoms}, optional={self.is_optional()}>'
        return s
    
    def __iter__(self):
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
        print('Warning: Your optional pattern chunk contains no column name atom, '
              'fall back to normal non-optional chunk.')
        return get_pattern_chunk(atoms)
    return PatternChunk(atoms, optional=True)

Pattern = List[PatternChunk]

def decode_pattern_string(pattern_string: str) -> Pattern:
    """Break down a pattern string into a pattern list for iteration.
    """
    validate_pattern_string(pattern_string)
    
    pattern = []
    curr_string = ''
    curr_atoms = []
    in_colname_atom = False
    in_optional_chunk = False
    escape = False
    for c in pattern_string:
        if c == '\\' and not escape:
            escape = True
            continue
        elif c == '$' and not escape:
            if not in_colname_atom:
                if curr_string != '':
                    curr_atoms.append(LiteralAtom(curr_string))
                    curr_string = ''
                in_colname_atom = True
            else:
                if curr_string != '':
                    curr_atoms.append(ColumnNameAtom(curr_string))
                    curr_string = ''
                in_colname_atom = False
        elif c == '[' and not escape:
            if curr_string != '':
                curr_atoms.append(LiteralAtom(curr_string))
                curr_string = ''
            if curr_atoms != []:
                pattern.append(get_pattern_chunk(curr_atoms))
                curr_atoms = []
            in_optional_chunk = True
        elif c == ']' and not escape:
            if curr_string != '':
                curr_atoms.append(LiteralAtom(curr_string))
                curr_string = ''
            if curr_atoms != []:
                pattern.append(get_optional_pattern_chunk(curr_atoms))
                curr_atoms = []
            in_optional_chunk = False
        else:
            curr_string += c
            escape = False
    if curr_string != '':
        curr_atoms.append(LiteralAtom(curr_string))
    if curr_atoms != []:
        pattern.append(get_pattern_chunk(curr_atoms))
    return pattern

def validate_pattern_string(s: str) -> None:
    def check_dollar(s):
        escape = False
        unpaired_dollar = False
        for c in s:
            if c == '$' and not escape:
                if unpaired_dollar:
                    unpaired_dollar = False
                else:
                    unpaired_dollar = True
            if c in '[]' and not escape and unpaired_dollar:
                raise ValueError('Invalid Pattern String: Brackets "[]" inside $$ key.')
        assert not unpaired_dollar, 'Invalid Pattern String: Dangling "$"'
        
    def check_bracket(s):
        escape = False
        previous_bracket = ']'
        for c in s:
            if c == '\\' and not escape:
                escape = True
                continue
            if c == '[' and not escape:
                assert previous_bracket != '[', 'Invalid Pattern String: Nested "["'
                previous_bracket = c
            elif c == ']' and not escape:
                assert previous_bracket == '[', 'Invalid Pattern String: Dangling "["'
                previous_bracket = c
            escape = False
        assert previous_bracket != '[', 'Invalid Pattern String: Dangling "["'
    
    check_dollar(s)
    check_bracket(s)
        

if __name__ == '__main__':
    s = '$颁发时间$, $项目$[/$奖项$], $机构$[/$级别$]'
    decode = decode_pattern_string(s)
    pprint(decode)