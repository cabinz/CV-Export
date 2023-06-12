本项目用于在记录存档个人履历（如获奖、荣誉、任职经历等）的同时，能够按照模式要求直接导出格式化的文本，便于在申请表、简历中相关栏目进行填写。

本项目的起因是：时常有信息表格需要填写个人履历，不同表格对各项内容的格式、顺序都有不同要求，在条目较多时逐条整理十分麻烦。通过这个项目，现在只要在本地维护一份详细的数据表就可以实现按照要求提取信息并自动格式化输出。

推荐使用的方法为：
- 在本地，将所有的个人经历项目记录在excel表中（每行为一个数据项目，不同的列记录各种相关信息，如项目名称、奖项、获奖时间等），同时可以将相关联的电子证明材料都存整理到文件夹中，并在excel表里进行记录；
- 通过编写简单的脚本来按照要求导出所需要的格式化文本。

如运行示例文件 `run-分类.py` 可以导出文本文件包含类似内容：
```
Export finishing time: 2023-06-12 17:07:18.142427
=======竞赛=======
2022年08月, 大学生计算机系统能力大赛/二等奖, xx计算机教育研究会/国家级
2020年04月, 美国大学生数学建模竞赛/一等奖, 美国数学及其应用联合会/国家级
=======荣誉称号=======
2022年12月, 2021-2022年度 优秀学生标兵, xx大学/校级
2021年04月, 优秀学生奖, xxx基金会/校级
2020年10月, xxxx级军训/优秀学员, xx大学/校级
=======社会实践=======
2020年11月, xxx招生组成果奖/三等奖, xx大学/校级
=======奖学金=======
2022年10月, 国家奖学金, 教育部/国家级
2022年03月, 本科生奖学金/一等奖, xx大学/校级
2021年12月, xx集团奖学金, xx集团/社会捐助奖学金
=======实习=======
2022-2023, 软件实习, 香蕉研发有限公司
2021-2022, 科研实习, xx大学计算机科学系
=======志愿服务=======
2019-2020-1, 图书义卖, 志愿者协会
2019-2020-1, 垃圾分类知识宣传, 志愿者协会
```

脚本接口接收处理的是`pandas.DataFrame`类型的对象，所以只要数据表能够被pandas库加载即可，不一定要使用excel表格进行记录（也可以使用如.csv等其它格式的文件）。

# 项目结构

- `decode.py` 模块用于解析pattern字符串；
- `cv_export.py` 模块用于按照pattern的模式，对给定的`pandas.DataFrame`对象进行处理；
- `run-分类.py` 和 `run-分级.py`均为用户脚本示例。


# 依赖

```
python >= 3.6
pandas==1.5.3
openpyxl==3.0.10
```

# 使用

`run-分类.py` 和 `run-分级.py`均为用户脚本示例。

用户只需要在自己的脚本中通过
```python
import cv_export
```
引入所需要的数据类和方法，并通过pandas读入并筛选得到希望输出的DataFrame数据块对象，定义需要的pattern符串，通过`cv_export.stringify_data_blk()` 就可以逐行格式化打印整个数据块。


## Pattern字符串语法

- 用dollar符号`$`包围的是数据的列名，被称为**列名原子**；对于每个列名原子，会读取每个数据行中对应对列，填入生成文本的对应位置；除了列名，还有一个特殊的列名原子 `$编号$`，用于给每条生成的数据自动编号；
- 如果要对列名原子读去的内容进行额外的变换，填写变换后的内容，需要编写对应的handler函数；
- 用中括号括起来的内容是**可选区段**，其中必须包括至少一个dollar值；对于每条数据的每个可选区段，会检查其内所有dollar值，若有任何一个dollar值对应的位置没有数据，则整个可选区段会被省略；
- 如果要直接打印 中括号 和 dollar符号，需要使用`\`进行转义，也即使用`\[`, `\]`, `\$`；要直接打印一个斜杠，同样需要转义`\\`
- 除了上述内容外，其余pattern字符串中的内容会被在每一行数据文本中被直接打印
如
```python
pattern_string = '($编号$) $颁发时间$, $项目$[/$奖项$], $机构$/$级别$'
```
可能会打印出
```
"(1) 2022年10月, 国家奖学金, 教育部/国家级"
或
"(1) 2020年04月, 学习奖学金/三等奖, xx大学/校级"
```

## Handler编写

最常见的情况是需要定制不同的时间数据的格式，修改下列的代码可以按照要求对日期时间等重新格式化：

```python
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
    '颁发时间': time_handler, # 指定'颁发时间'列使用自定义的handler重新格式化
}

s = stringify_data_blk(data_blk, pattern, colname2handler=customized_handlers)

print(s)
```

打印结果可以看到时间部分的内容被重新格式化：

```
=======国家级=======
1. 2022年的10月31日, 国家奖学金, 教育部
2. 2022年的08月23日, 大学生计算机系统能力大赛(二等奖), xx计算机教育研究会
3. 2020年的04月28日, 美国大学生数学建模竞赛(一等奖), 美国数学及其应用联合会
=======校级=======
1. 2022年的12月20日, 2021-2022年度 优秀学生标兵, xx大学
2. 2022年的03月31日, 本科生奖学金(一等奖), xx大学
3. 2021年的04月26日, 优秀学生奖, xxx基金会
4. 2020年的11月01日, xxx招生组成果奖(三等奖), xx大学
5. 2020年的10月01日, xxxx级军训(优秀学员), xx大学
=======社会捐助奖学金=======
1. 2021年的12月28日, xx集团奖学金, xx集团
```
