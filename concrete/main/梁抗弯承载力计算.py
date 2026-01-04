# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd
from datetime import datetime

# 添加项目根目录到sys.path，确保能找到concrete模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# 导入核心计算/报告模块
from concrete.core.beam_rect_fc import beam_rect_fc
from concrete.core.beam_t_fc import beam_t_fc
from concrete.core.report_beam import report_beam_rect_fc, report_beam_t_fc

# 导入配置和工具函数
from concrete.config import (
    EXCEL_INPUT_PATH,
    EXCEL_OUTPUT_PATH,
    OUTPUT_DIR,
    GAMMA_RE,
    OUTPUT_COLS
)
from concrete.core.beam_utils import (
    validate_file_exists,
    read_excel_data,
    prepare_calculation_data,
    save_excel_result_with_style
)


def calculate_single_item(item, index, total_count):
    """
    计算单个数据项
    :param item: 计算参数项
    :param index: 索引
    :param total_count: 总数量
    :return: tuple - (x, Mu, M, rs_ratio, report, error_msg)
    """
    sec_num = item["sec_num"] if not pd.isna(item["sec_num"]) else ""
    gamma_0 = item["γ0"]
    M = item["M"]  # 弯矩设计值
    sec_num_display = f"序号：{total_count}.{index + 1}      编号：{sec_num}      截面类型：{item['sec_type']}"
    calc_p = item["calc_params"]

    try:
        if item["sec_type"] == "矩形":
            rect_calc_p = calc_p[0:2] + calc_p[4:]  # 跳过bf和hf
            result = beam_rect_fc(*rect_calc_p)
            x = result[0]
            Mu = result[4]
            # 计算抗力效应比R/S：地震作用组合时使用MuE/M，否则使用Mu/M
            is_seismic = item["is_seismic"]
            MuE = Mu / GAMMA_RE
            rs_ratio = (MuE / M if is_seismic == 1 else Mu / M) if M > 0 else 0
            # 创建包含M和rs_ratio的扩展结果
            extended_result = result + (M, rs_ratio)
            report = report_beam_rect_fc(sec_num_display, rect_calc_p, extended_result)
            return x, Mu, M, rs_ratio, report, None

        elif item["sec_type"] == "T形":
            result = beam_t_fc(*calc_p)
            x = result[1]
            Mu = result[5]
            # 计算抗力效应比R/S：地震作用组合时使用MuE/M，否则使用Mu/M
            is_seismic = item["is_seismic"]
            MuE = Mu / GAMMA_RE
            rs_ratio = (MuE / M if is_seismic == 1 else Mu / M) if M > 0 else 0
            # 创建包含M和rs_ratio的扩展结果
            extended_result = result + (M, rs_ratio)
            report = report_beam_t_fc(sec_num_display, calc_p, extended_result)
            return x, Mu, M, rs_ratio, report, None

        else:
            error_msg = f"第{index + 1}行：截面类型'{item['sec_type']}'不支持"
            report = f"【错误】{error_msg}"
            return 0, 0, 0, 0, report, error_msg

    except Exception as e:
        error_msg = f"第{index + 1}行：{str(e)}"
        report = f"【错误】{error_msg}"
        return 0, 0, 0, 0, report, error_msg


def main():
    """
    主函数
    """
    print("🚀 梁抗弯承载力计算程序启动...")
    start_time = datetime.now()

    # -------------------------- 读取Excel A-P列数据 --------------------------
    print("📖 正在读取Excel文件...")
    validate_file_exists(EXCEL_INPUT_PATH)
    df_input = read_excel_data(EXCEL_INPUT_PATH)

    # -------------------------- 准备计算数据 --------------------------
    param, result_data = prepare_calculation_data(df_input)

    if len(param) == 0:
        print("❌ 未找到有效计算数据，程序终止")
        sys.exit()

    print(f"📊 发现 {len(param)} 组待计算数据")

    # -------------------------- 生成OUT结果文件 --------------------------
    target_dir = OUTPUT_DIR
    os.makedirs(target_dir, exist_ok=True)
    file_name = "梁抗弯承载力计算结果.out"
    file_path = os.path.join(target_dir, file_name)

    local_time = start_time.strftime("%Y-%m-%d %H:%M:%S")

    print("🔄 开始计算...")
    error_count = 0

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"{'*' * 52}\n")
        f.write(f"计算时间：{local_time}\n")
        f.write(f"共{len(param)}组截面梁计算数据\n")
        f.write(f"{'*' * 52}\n")

        # 计算每行数据
        for idx, item in enumerate(param):
            # 计算单个数据项
            x, Mu, M, rs_ratio, report, error_msg = calculate_single_item(item, idx, len(param))

            # 记录错误
            if error_msg:
                error_count += 1
                print(f"  ⚠️ {error_msg}")

            # 计算抗震承载力
            MuE = Mu / GAMMA_RE

            # 填充Q-T列结果
            result_data[idx][OUTPUT_COLS["x_col"]] = round(x, 3)
            result_data[idx][OUTPUT_COLS["mu_col"]] = round(Mu, 2)
            result_data[idx][OUTPUT_COLS["mue_col"]] = round(MuE, 2)
            result_data[idx][OUTPUT_COLS["rs_col"]] = round(rs_ratio, 2)

            # 写入out文件
            f.write(report + "\n")

        # 写入总结信息
        f.write(f"\n{'=' * 60}\n")
        f.write(f"计算完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总计: {len(param)} 组数据，其中 {error_count} 组计算出错\n")
        f.write(f"结果文件: {file_path}\n")

    print(f"✅ 计算完成，生成报告文件: {file_path}")
    if error_count > 0:
        print(f"⚠️  注意: 有 {error_count} 组数据计算出错，请查看报告文件")

    # -------------------------- 生成Excel结果文件 --------------------------
    print("💾 正在保存Excel结果...")
    save_excel_result_with_style(result_data, EXCEL_OUTPUT_PATH, EXCEL_INPUT_PATH)
    print("💾 Excel结果文件保存完毕")
    # -------------------------- 程序结束 --------------------------
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"\n🎉 程序执行完毕!")
    print(f"⏱️  总耗时: {duration:.1f}秒")
    print(f"📈 数据处理: {len(param)} 行")
    print(f"📁 输出文件:")
    print(f"   📄 Excel结果: {EXCEL_OUTPUT_PATH}")
    print(f"   📄 详细报告: {file_path}")


if __name__ == "__main__":
    main()