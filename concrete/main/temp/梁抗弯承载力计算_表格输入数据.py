import sys
import os
from datetime import datetime
import pandas as pd  # 新增：导入读取Excel的库

# 导入模块（保持不变）
from concrete.core.beam_rect_fc import beam_rect_fc
from concrete.core.report_beam_rect import report_beam_rect_fc

# -------------------------- 核心修改：从Excel读取参数 --------------------------
# 1. 定义Excel文件路径（与项目结构匹配，避免硬编码绝对路径）
excel_path = r"/input/梁抗弯承载力数据文件.xlsx"  # 用r前缀避免转义问题

# 2. 检查Excel文件是否存在（避免路径错误导致报错）
if not os.path.exists(excel_path):
    print(f"❌ 未找到Excel文件！请确认文件路径：{excel_path}")
    sys.exit()  # 若文件不存在，终止程序并提示

# 2. 检查Excel文件是否存在（避免路径错误导致报错）
if not os.path.exists(excel_path):
    print(f"❌ 未找到Excel文件！请确认文件路径：{excel_path}")
    sys.exit()  # 若文件不存在，终止程序并提示

# 3. 读取Excel数据（指定Sheet1，按列名匹配数据）
# 列名对应关系：Excel列 → 计算参数（顺序需严格匹配）
df = pd.read_excel(
    excel_path,
    sheet_name="Sheet1",  # 读取Excel的Sheet1工作表
    usecols=["编号", "b", "h", "混凝土强度等级C", "受拉钢筋强度等级", "受压钢筋强度等级", "受拉钢筋面积As",
             "受拉钢筋as", "受压钢筋面积As", "受压钢筋as"],
    engine="openpyxl"  # 明确使用openpyxl引擎读取.xlsx文件
)

# 4. 将Excel数据转换为原代码的param格式（列表+字典）
param = []
for index, row in df.iterrows():  # 逐行遍历Excel数据
    # 跳过空行（若Excel中有空行，避免报错）
    if pd.isna(row["编号"]):
        continue

    # 按计算逻辑组织参数（顺序与beam_rect_fc函数参数要求一致）
    param_item = {
        "sec_id": str(row["编号"]),  # sec_id使用Excel中的"编号"列（转为字符串避免格式问题）
        "calc_params": [
            row["b"],  # 截面宽度b
            row["h"],  # 截面高度h
            row["混凝土强度等级C"],  # 混凝土强度等级
            row["受拉钢筋强度等级"],  # 受拉钢筋强度等级
            row["受压钢筋强度等级"],  # 受压钢筋强度等级
            row["受拉钢筋面积As"],  # 受拉钢筋面积As
            row["受拉钢筋as"],  # 受拉钢筋合力点到截面边缘距离as
            row["受压钢筋面积As"],  # 受压钢筋面积As'
            row["受压钢筋as"]  # 受压钢筋合力点到截面边缘距离as'
        ]
    }
    param.append(param_item)

# 若Excel中无有效数据，提示并终止
if len(param) == 0:
    print("❌ Excel文件中无有效计算数据，请检查Sheet1内容！")
    sys.exit()

# -------------------------- 以下代码保持原逻辑不变 --------------------------
count_rect = len(param)  # 计算参数组数（从Excel读取的有效行数）

# 定义结果文件路径（保持不变）
target_dir = r"/output"
os.makedirs(target_dir, exist_ok=True)
file_name = "梁抗弯承载力计算结果.out"
file_path = os.path.join(target_dir, file_name)

# 定义计算时间（保持不变）
dt = datetime.now()
local_time = dt.strftime("%Y-%m-%d %H:%M:%S")

# 写入结果文件并打印（保持不变）
with open(file_path, "w", encoding="utf-8") as f:
    f.write(f"{'*' * 52}\n")
    f.write(f"计算时间：{local_time}\n")
    f.write(f"共{count_rect}组矩形截面梁计算数据\n")  # 新增：显示数据组数
    f.write(f"{'*' * 52}\n\n")

    num = 1  # 计算顺序序号
    for item in param:
        # 生成截面标识（使用Excel中的编号）
        sec_id = f"序号{count_rect}.{num}      编号：{item['sec_id']}"
        calc_p = item["calc_params"]

        # 调用计算函数（保持不变）
        result = beam_rect_fc(*calc_p)
        report = report_beam_rect_fc(sec_id, calc_p, result)

        # 打印到控制台并写入文件（保持不变）
        print(report)
        f.write(report + "\n\n")  # 加空行优化阅读格式
        num += 1

    end_str = f"\n【END】计算完成，共{count_rect}组数据，结果已保存至：{file_path}"
    print(end_str)
    f.write(end_str)

# 控制台提示（保持不变）
print(f"\n✅ 计算结果已写入文件：{file_path}")