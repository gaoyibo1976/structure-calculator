import pandas as pd
import sys
import os

# ===================== 1. 动态获取项目根目录（核心修复：替代硬编码） =====================
# 当前批量脚本的绝对路径（main目录下的批量计算文件）
current_script_path = os.path.abspath(__file__)
# 当前脚本所在目录（main目录）
current_dir = os.path.dirname(current_script_path)
# 项目根目录（main的上一级，即包含main、modules的目录）
PROJECT_ROOT = os.path.dirname(current_dir)
# 将根目录加入Python搜索路径（确保能找到modules、main目录）
sys.path.append(PROJECT_ROOT)

# ===================== 2. 修正导入路径（核心修复：匹配实际文件位置） =====================
try:
    # 导入main目录下的「单筋矩形截面梁抗弯承载力.py」中的gen_report2
    from main.单筋矩形截面梁抗弯承载力 import gen_report2
    # 导入modules目录下的calc_rect_fc.py中的核心函数
    from modules.calc_rect_fc import (
        calc_formula,
        gen_param,
        calc_intermediate_params
    )
except ImportError as e:
    raise ImportError(f"导入失败！请检查文件路径/函数名：{e}\n"
                      f"项目根目录：{PROJECT_ROOT}\n"
                      f"当前脚本目录：{current_dir}")

# ===================== 3. 批量计算核心函数（完整逻辑） =====================
def batch_calc_from_excel(excel_path, out_txt_path="out.txt"):
    """
    从Excel批量读取参数 → 调用modules/calc_rect_fc.py计算 → 输出到out.txt
    :param excel_path: Excel参数文件路径（相对/绝对路径均可）
    :param out_txt_path: 输出out格式文本文件路径
    """
    # 校验Excel文件是否存在
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel文件不存在：{excel_path}")

    # 读取Excel参数（sheet_name=0取第一个工作表）
    try:
        df = pd.read_excel(excel_path, sheet_name=0)
    except Exception as e:
        raise RuntimeError(f"读取Excel失败：{e}（请检查文件格式/列名）")

    # 校验Excel必要列（需与calc_rect_fc.py的参数要求一致）
    required_cols = ['α1', 'fc', 'b', 'h0', 'a2', 'fy', 'As', 'M', 'ξb']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Excel缺少必需列：{missing_cols}\n"
                         f"当前Excel列名：{list(df.columns)}")

    # 批量遍历计算
    all_reports = []
    total_rows = len(df)
    all_reports.append(f"矩形截面梁抗弯承载力批量计算结果\n总计{total_rows}行数据\n{'='*80}")

    for idx, row in df.iterrows():
        row_num = idx + 1
        try:
            # 构造参数字典（直接传给calc_rect_fc.py的函数）
            p = {
                'α1': row['α1'],
                'fc': row['fc'],
                'b': row['b'],
                'a2': row['a2'],
                'fy': row['fy']
            }
            r = {
                'h0': row['h0'],
                'As': row['As'],
                'ξb': row['ξb']
            }
            M = row['M']  # 计算弯矩

            # 调用modules/calc_rect_fc.py中的中间参数计算函数
            calc_intermediate_params(p, r, M)

            # 调用gen_report2生成计算书（依赖calc_rect_fc.py的函数）
            report = gen_report2(p, r, M, r['x_calc'])

            # 记录该行结果
            all_reports.append(f"\n===== 第{row_num}行（共{total_rows}行）计算结果 =====\n{report}")
            print(f"✅ 第{row_num}行计算完成")

        except Exception as e:
            # 记录错误信息（不中断批量计算）
            error_msg = f"\n===== 第{row_num}行计算失败 =====\n错误详情：{str(e)}\n{'='*50}"
            all_reports.append(error_msg)
            print(f"❌ 第{row_num}行计算失败：{e}")

    # 输出到out格式文本文件（UTF-8编码避免中文乱码）
    try:
        with open(out_txt_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(all_reports))
        print(f"\n📄 批量计算完成！结果文件路径：{os.path.abspath(out_txt_path)}")
    except Exception as e:
        raise RuntimeError(f"写入out文件失败：{e}")

# ===================== 4. 调用入口（自定义Excel路径） =====================
if __name__ == "__main__":
    # -------------------------- 请修改此处路径 --------------------------
    # Excel参数文件路径（可填相对/绝对路径，示例：项目根目录下的「梁抗弯计算参数.xlsx」）
    EXCEL_FILE_PATH = os.path.join(PROJECT_ROOT, "梁抗弯计算参数.xlsx")
    # 输出out文件路径（默认项目根目录下的out.txt）
    OUT_TXT_PATH = os.path.join(PROJECT_ROOT, "out.txt")
    # -------------------------------------------------------------------

    # 执行批量计算
    try:
        batch_calc_from_excel(EXCEL_FILE_PATH, OUT_TXT_PATH)
    except Exception as e:
        print(f"\n❌ 批量计算总异常：{e}")
        sys.exit(1)