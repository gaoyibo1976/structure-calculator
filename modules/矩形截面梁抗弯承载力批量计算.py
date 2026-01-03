import pandas as pd
import sys
import os

# 添加calc_rect_fc.py所在目录到Python路径
modules_dir = os.path.dirname(r"D:\My Python\工程结构计算平台\modules\矩形截面梁抗弯承载力计算数据文件.xlsx")
sys.path.append(modules_dir)

# 导入计算函数
from beam_rect_fc import beam_rect_fc


def batch_calculate_beam():
    # 1. 数据文件路径
    excel_path = r"D:\My Python\工程结构计算平台\modules\矩形截面梁抗弯承载力计算数据文件.xlsx"

    # 2. 读取Excel数据（新增读取编号列）
    try:
        df = pd.read_excel(excel_path)
        # 提取编号列（假设列名为“编号”，若实际列名不同请修改此处）
        id_list = df['编号'].tolist()
        # 提取计算参数列
        data_cols = [
            'b', 'h', '混凝土强度等级C', '受拉钢筋强度等级',
            '受压钢筋强度等级', '受拉钢筋面积As', '受拉钢筋as',
            '受压钢筋面积As', '受压钢筋as'
        ]
        params_list = df[data_cols].values.tolist()

        # 校验编号和参数数量一致
        if len(id_list) != len(params_list):
            print("❌ 编号列和参数列数据行数不匹配！")
            return
        print(f"✅ 成功读取 {len(params_list)} 条计算数据（含编号）")
    except Exception as e:
        print(f"❌ 读取数据文件失败：{str(e)}")
        return

    # 3. 输出文件路径
    output_dir = os.path.dirname(excel_path)
    output_path = os.path.join(output_dir, "计算结果.out")

    # 4. 循环计算并写入结果（新增编号输出）
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # 遍历编号和对应参数（enumerate保留原索引，id_num是数据编号）
            for idx, (id_num, params) in enumerate(zip(id_list, params_list), start=1):
                try:
                    # ========== 提取本次计算的输入参数 ==========
                    b = params[0]  # 梁宽
                    h = params[1]  # 梁高
                    C_grade = params[2]  # 混凝土强度等级C
                    steel_t_grade = params[3]  # 受拉钢筋强度等级
                    steel_c_grade = params[4]  # 受压钢筋强度等级
                    As = params[5]  # 受拉钢筋面积As
                    as_ = params[6]  # 受拉钢筋重心距as
                    As_prime = params[7]  # 受压钢筋面积As'
                    as_prime = params[8]  # 受压钢筋重心距as'

                    # 调用函数，获取返回的元组
                    result_tuple = beam_rect_fc(*params)

                    # 调试：打印元组结构（确认后可删除）
                    print(f"第{idx}条（编号{id_num}）返回的元组内容：{result_tuple}")

                    # ========== 提取计算结果参数（保留1位小数） ==========
                    x = round(result_tuple[0], 1)  # 混凝土受压区高度
                    xb = round(result_tuple[1], 1)  # 界限相对受压区高度ξbh0
                    Mu = round(result_tuple[2], 1)  # 抗弯承载力
                    σsc = round(result_tuple[3], 1)  # 受压钢筋应力
                    σs = round(result_tuple[4], 1)  # 受拉钢筋应力

                    # ========== 按统一风格拼接编号+输入参数+计算结果 ==========
                    result_text = f"""【数据编号】{id_num}

【输入参数】
梁宽b={b}mm
梁高h={h}mm
混凝土强度等级C={C_grade}
受拉钢筋强度等级={steel_t_grade}
受压钢筋强度等级={steel_c_grade}
受拉钢筋面积As={As}mm²
受拉钢筋重心距as={as_}mm
受压钢筋面积As'={As_prime}mm²
受压钢筋重心距as'={as_prime}mm

【计算结果】
混凝土受压区高度x={x}mm
界限相对受压区高度ξbh0={xb}mm
抗弯承载力Mu={Mu}kN·m
受压钢筋应力σs'={σsc:.1f}N/mm²
受拉钢筋应力σs ={σs:.1f}N/mm²
"""

                    # 写入当前计算结果（加分隔符更易读）
                    f.write(f"===== 第{idx}条计算结果 =====\n")
                    f.write(result_text)
                    f.write("\n----------------------------------------\n\n")  # 分隔线
                    print(f"✅ 第{idx}条（编号{id_num}）计算完成")
                except Exception as e:
                    error_msg = f"第{idx}条（编号{id_num}）计算失败：{str(e)}\n\n"
                    f.write(error_msg)
                    print(f"❌ 第{idx}条（编号{id_num}）计算失败：{str(e)}")
    except Exception as e:
        print(f"❌ 写入结果文件失败：{str(e)}")
        return

    # 5. 计算结束
    print(f"\n📄 所有计算完成！结果文件路径：{output_path}")


if __name__ == "__main__":
    batch_calculate_beam()