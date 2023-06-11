本项目用于在记录存档个人获奖、荣誉、任职经历的同时，能够按照模式要求直接导出格式化的文本，便于在申请表、简历中相关栏目的填写。

推荐使用的方法为：
- 在本地，将所有的个人经历项目记录在excel表中（每行为一个数据项目，不同的列记录各种相关信息，如项目名称、奖项、获奖时间等），同时可以将相关联的电子证明材料都存整理到文件夹中，并在excel表里进行记录；
- 通过编写简单的脚本来按照要求导出所需要的格式化文本。

如运行示例文件 `run-分类.py` 可以导出文本文件包含类似内容：
```
Export finishing time: 2023-06-12 01:04:37.562761
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
pandas==1.1.5
```

# 使用

`run-分类.py` 和 `run-分级.py`均为用户脚本示例。

用户只需要在自己的脚本中通过
```python
import cv_export
```
引入所需要的数据类和方法，并通过pandas读入并筛选得到希望输出的DataFrame数据块对象，定义需要的pattern符串，通过`cv_export.stringify_data_blk()` 就可以逐行格式化打印整个数据块。


## Pattern字符串语法

- 用dollar符号包围的是数据行的列表头，会读取每个数据行的对应列并填入生成的文本，如果要指定填写的格式，需要编制对应的handler；
- 用中括号括起来的内容是可选区段，其中必须包括dollar值；对于每个数据行，会检查所有dollar值，若有任何一个dollar值对应的位置没有数据，则整个可选区段会被省略；
- 如果要直接打印中括号和dollar符号，需要使用"/"进行转义；要直接打印一个斜杠，同样需要转义"\\"

如
```python
pattern_string = '$颁发时间$, $项目$[/$奖项$], $机构$/$级别$'
```
可能会打印出
```
"2022年10月, 国家奖学金, 教育部/国家级"
或
"2020年04月, 学习奖学金/三等奖, xx大学/校级"
```


