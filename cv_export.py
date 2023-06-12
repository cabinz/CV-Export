from typing import List, Union
import pandas as pd 

from decode import decode_pattern_string
from decode import ColumnNameAtom, LiteralAtom, PatternChunk, Pattern


def default_handler(row, colname):
    assert not pd.isnull(row[colname]), (f'Null cell in column "{colname}".' 
        'Consider completing the data, '
        'or making the part of pattern optional (by adding bracket).')
    return row[colname]


def time_handler(row, colname):
    time = row[colname]
    s = '{}年{}月'.format(
        time.strftime("%Y"),
        time.strftime("%m"),
    )
    return s


def get_literal_handler(string):
    """anything -> a constant string."""
    
    if not isinstance(string, str):
        string = str(string)
    def hdlr(row, colname):
        return string
    return hdlr


DEFAULT_COLNAME2HANDLERS = {
    # '类别': None,  # eg. 奖学金，竞赛，荣誉称号，社会实践，实习
    # '项目': None,  # eg. 本科生奖学金，数学建模大赛
    # '奖项': None,  # eg. 一等奖，二等奖，三等奖
    # '级别': None,  # eg. 校级，省级，国家级，社会捐助奖学金
    # '机构': None,  # eg. 美国数学及其应用联合会
    # '开始时间': None,  # eg. 2021/7/1
    # '结束时间': None,  # eg. 2021/8/31
    # '时长': None,  # eg. 6h
    # '所属时期': None,  # eg. 2019-2020, 2019-2020-1
    '颁发时间': time_handler,  # eg. 2020/4/30
    # '颁发学期': None,  # eg. 2020-2021-1
}


def get_handler(colname: str, row_idx: int, colname2handler=DEFAULT_COLNAME2HANDLERS):
    """Retrieve a hanlder for a ColumnNameAtom (CNA).
    
    Only ColumnNameAtom needs handler. LiteralAtom will be directly printed.
    By Default, a CNA indicates to extract content of a cell from a data row by `default_hanlder()` 
    and directly filled in the place.
    
    If extra transformation is needed on the extract raw content before filling, 
    a handler bound with the column name kay should be added into the `colname2hanlder` mapping arg, 
    to define the required transformation.

    Args:
        colname (str): The column name (for indexing on the `colname2hanlder` mapping).
        row_idx (int): Index of the current data row.
        colname2handler (mapping, optional): Map column names to customized handlers. 
            Defaults to DEFAULT_COLNAME2HANDLERS.

    Returns:
        _type_: _description_
    """
    if colname == '编号':
        return get_literal_handler(row_idx)
    elif colname in colname2handler.keys():
        return colname2handler[colname]
    else:
        return default_handler


def handle_chunk(pattern_chunk: PatternChunk, row, row_idx, colname2handler):
    def is_required_optional_chunk(chunk, row) -> bool:
        """Check if the optional chunk has non-existing atom required.
        If so, the optional chunk can be just ignored in the output."""
        for atom in chunk:
            if isinstance(atom, ColumnNameAtom):
                if pd.isnull(row[atom.colname]):
                    return False
        return True
    
    if pattern_chunk.is_optional() and not is_required_optional_chunk(pattern_chunk, row):
        return ''
    
    s = ''
    for atom in pattern_chunk:
        if isinstance(atom, ColumnNameAtom):
            handler = get_handler(atom.colname, row_idx, colname2handler)
            s += handler(row, atom.colname)
        elif isinstance(atom, LiteralAtom):
            s += atom.string
        else:
            raise TypeError(f'Unexpected PatternAtom: type = {type(atom)}')
    return s
    

def stringify_data_row(row, pattern: Pattern, row_idx, colname2handler, newline=True) -> str:
    s = ''
    check_colnames(pattern, row)
    for chunk in pattern:
        s += handle_chunk(chunk, row, row_idx, colname2handler)
    s += '\n' if newline else ''
    return s


def stringify_data_blk(blk: pd.DataFrame, pattern: str, 
                      colname2handler=DEFAULT_COLNAME2HANDLERS, newline=True,
                      col_for_sorting: str = None, ascending: bool = False) -> str:
    pattern = decode_pattern_string(pattern)
    if col_for_sorting:
        blk = blk.sort_values(col_for_sorting, ascending=ascending, ignore_index=True)

    ret = ''
    for i, row in blk.iterrows():
        ret += stringify_data_row(row, pattern, i+1, colname2handler, newline=newline)
    return ret


def check_colnames(pattern: Pattern, row):
    def check_colname(colname: str, row):
        assert (colname in row.index) or (colname == '编号'), \
            f'Column name "{colname}" does not exist in the data.'
    
    for chunk in pattern:
        for atom in chunk:
            if isinstance(atom, ColumnNameAtom):
                check_colname(atom.colname, row)