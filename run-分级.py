from cv_export import *
from pathlib import Path
from datetime import datetime

########### Import data ###########
DATA_PATH = './record-example.xlsx'
df = pd.read_excel(DATA_PATH)
# Filter out desired data rows.
df = df[
    (df["类别"] == "竞赛") |
    (df["类别"] == "奖学金") |
    (df["类别"] == "荣誉称号") |
    (df["类别"] == "社会实践")
]

########### Run ###########
s_final = ''


"""List out by category along a specified column.
"""
# Spilt the output according to different category '类别', '级别', or others
cat_col = '级别'
cats_to_extract = df[cat_col].unique()

# Define patterns.
time_pattern = '$编号$. $颁发时间$, $项目$[($奖项$)], $机构$'

# Define hanlders.
def time_handler(row, colname):
    """
    Reformat time data into '%Y年的%m月%d日'
    """
    time = row[colname]
    s = '{}年的{}月{}日'.format(
        time.strftime('%Y'),
        time.strftime('%m'),
        time.strftime('%d'),
    ) # Transform (reformat) the cell content.
    return s
    
customized_handlers = {
    '颁发时间': time_handler,
}

# Print.
for cat in cats_to_extract:
    s_final += "="*7 + f"{cat}" + "="*7 + "\n"
    blk = df[df[cat_col] == cat]  # extract a block of a category
    s_final += stringify_data_blk(blk, time_pattern, 
                                  colname2handler=customized_handlers, 
                                  col_for_sorting='颁发时间')
    
print(s_final)
