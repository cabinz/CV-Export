from typing import List, Union
import pandas as pd 

from decode import decode_pattern_string
from decode import Pattern, ColumnNameAtom, LiteralAtom, PatternChunk


def identical_handler(row, colname):
    return row[colname]


def time_handler(row, colname):
    time = row[colname]
    s = '{}年{}月'.format(
        time.strftime("%Y"),
        time.strftime("%m"),
    )
    return s


def literal_handler(string):
    """anything -> a constant string."""
    def hdlr(row, colname):
        return string
    return hdlr


DEFAULT_COLNAME2HANDLERS = {
    '类别': None,  # eg. 奖学金，竞赛，荣誉称号，社会实践，实习
    '项目': None,  # eg. 本科生奖学金，数学建模大赛
    '奖项': None,  # eg. 一等奖，二等奖，三等奖
    '级别': None,  # eg. 校级，省级，国家级，社会捐助奖学金
    '机构': None,  # eg. 美国数学及其应用联合会
    '开始时间': None,  # eg. 2021/7/1
    '结束时间': None,  # eg. 2021/8/31
    '时长': None,  # eg. 6h
    '所属时期': None,  # eg. 2019-2020, 2019-2020-1
    '颁发时间': time_handler,  # eg. 2020/4/30
    '颁发学期': None,  # eg. 2020-2021-1
}


def get_handler(colname: str, row_idx: int, colname2handler=DEFAULT_COLNAME2HANDLERS):
    if colname == '编号':
        return literal_handler(row_idx)
    elif colname in colname2handler.keys():
        handler = colname2handler[colname]
        return handler if handler else identical_handler
    else:
        raise ValueError(f'The column name "{colname}" is not in the hanlder mapping keys.')


def handle_chunk(pattern_chunk: PatternChunk, row, row_idx):
    def is_required_optional_chunk(chunk, row) -> bool:
        """Check if the optional chunk has non-existing atom required.
        If so, the optional chunk can be just ignored in the output."""
        for atom in chunk:
            if isinstance(atom, ColumnNameAtom) and pd.isnull(row[atom.colnanme]):
                return False
        return True
    
    if pattern_chunk.is_optional() and not is_required_optional_chunk(pattern_chunk, row):
        return ''
    
    s = ''
    for atom in pattern_chunk:
        if isinstance(atom, ColumnNameAtom):
            handler = get_handler(atom.colnanme, row_idx)
            s += handler(row, atom.colnanme)
        elif isinstance(atom, LiteralAtom):
            s += atom.string
        else:
            raise TypeError(f'Unexpected PatternAtom type: {type(atom)}')
    return s
    

def stringify_data_row(row, pattern: Pattern, row_idx, handler_map, new_line=True) -> str:
    s = ''
    for chunk in pattern:
        s += handle_chunk(chunk, row, row_idx)
    s += '\n' if new_line else ''
    return s


def stringify_data_blk(blk: pd.DataFrame, pattern: str, 
                      handler_map=DEFAULT_COLNAME2HANDLERS,
                      col_for_sorting: str = None, ascending: bool = False) -> str:
    pattern = decode_pattern_string(pattern)
    if col_for_sorting:
        blk = blk.sort_values(col_for_sorting, ascending=ascending, ignore_index=True)

    ret = ''
    for i, row in blk.iterrows():
        ret += stringify_data_row(row, pattern, row_idx=i, handler_map=handler_map)
    return ret

