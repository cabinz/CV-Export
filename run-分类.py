from cv_export import *
from pathlib import Path
from datetime import datetime

########### Config ###########
RES_ON_CONSOLE = False
OUTPUT_TO_FILE = True
OUT_DIR = Path('.')
TIMESTAMP = datetime.now().strftime('%Y%m%d-%H%M%S')

########### Import data ###########
DATA_PATH = './record-example.xlsx'
df = pd.read_excel(DATA_PATH)

########### Run ###########
s_final = ''


"""List out by category along a specified column.
"""
# Spilt the output according to different category '类别', '级别', or others
cat_col = '类别'
cats_to_extract = df[cat_col].unique()

# Define patterns
time_pattern = '$颁发时间$, $项目$[/$奖项$], $机构$[/$级别$]'
period_pattern = '$所属时期$, $项目$, $机构$'

for cat in cats_to_extract:
    s_final += "="*7 + f"{cat}" + "="*7 + "\n"
    blk = df[df[cat_col] == cat]  # extract a block of a category
    if cat in ('竞赛', '社会实践', '奖学金', '荣誉称号', '大创'):
        s_final += stringify_data_blk(blk, time_pattern, col_for_sorting='颁发时间')
    elif cat in ('实习', '志愿服务', '任职'):
        s_final += stringify_data_blk(blk, period_pattern, col_for_sorting='所属时期')
        

# Output
if RES_ON_CONSOLE:
    print(s_final)
if OUTPUT_TO_FILE:
    out_path = OUT_DIR / f'分类-{TIMESTAMP}.out'
    with out_path.open('x', encoding='utf-8') as outfile:
        outfile.write(f'Export finishing time: {datetime.now()}\n')
        outfile.write(s_final)
    print(f'The output is stored in file {out_path}')
