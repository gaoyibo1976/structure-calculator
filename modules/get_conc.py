def get_delta(f_cuk):
    """
    根据混凝土立方体抗压强度f_cuk，通过线性插值/外推获取变异系数δ（来自表1）
    支持任意数值输入，对极端值采用趋势外推
    """
    # 基础δ值数据（来自表1：f_cuk对应强度等级，δ为表中取值）
    delta_data = {
        15: 0.21,   # C15对应f_cuk=15，δ=0.21
        20: 0.18,   # C20对应f_cuk=20，δ=0.18
        25: 0.16,   # C25对应f_cuk=25，δ=0.16
        30: 0.14,   # C30对应f_cuk=30，δ=0.14
        35: 0.13,   # C35对应f_cuk=35，δ=0.13
        40: 0.12,   # C40对应f_cuk=40，δ=0.12
        45: 0.12,   # C45对应f_cuk=45，δ=0.12
        50: 0.11,   # C50对应f_cuk=50，δ=0.11
        55: 0.11,   # C55对应f_cuk=55，δ=0.11
        60: 0.10,   # C60对应f_cuk=60，δ=0.10
        65: 0.10,   # C65对应f_cuk=65，δ=0.10
        70: 0.10,   # C70对应f_cuk=70，δ=0.10
        75: 0.10,   # C75对应f_cuk=75，δ=0.10
        80: 0.10    # C80对应f_cuk=80，δ=0.10
    }
    sorted_f = sorted(delta_data.keys())  # 排序后的f_cuk：[15,20,25,30,35,40,45,50,55,60,65,70,75,80]
    min_f, max_f = sorted_f[0], sorted_f[-1]  # 最小f_cuk=15，最大f_cuk=80

    # 情况1：f_cuk在表1的规范值中，直接返回对应的δ
    if f_cuk in delta_data:
        return delta_data[f_cuk]

    # 情况2：f_cuk小于最小值（15）：按前两个规范点（15→20）的斜率外推
    if f_cuk < min_f:
        slope = (delta_data[sorted_f[1]] - delta_data[sorted_f[0]]) / (sorted_f[1] - sorted_f[0])
        delta = delta_data[min_f] + slope * (f_cuk - min_f)
        return delta

    # 情况3：f_cuk大于最大值（80）：按最后两个规范点（75→80）的斜率外推（二者δ均为0.10，斜率为0）
    if f_cuk > max_f:
        slope = (delta_data[sorted_f[-1]] - delta_data[sorted_f[-2]]) / (sorted_f[-1] - sorted_f[-2])
        delta = delta_data[max_f] + slope * (f_cuk - max_f)
        return delta

    # 情况4：f_cuk在表1的规范值之间，线性插值
    for i in range(len(sorted_f)):
        if sorted_f[i] > f_cuk:
            # 找到当前f_cuk的上下界规范值
            lower_f, upper_f = sorted_f[i-1], sorted_f[i]
            lower_delta, upper_delta = delta_data[lower_f], delta_data[upper_f]
            # 线性插值公式
            delta = lower_delta + (upper_delta - lower_delta) * (f_cuk - lower_f) / (upper_f - lower_f)
            return delta
    return None

def get_concrete_core_indices(f_cuk):
    """
    核心函数：返回五个核心设计指标（供其他py文件调用）
    参数：f_cuk - 混凝土立方体抗压强度标准值
    返回：元组 (f_tk, f_t, f_ck, f_c, E_c)
          分别对应：轴心抗拉强度标准值、轴心抗拉强度设计值、
                  轴心抗压强度标准值、轴心抗压强度设计值、弹性模量
    """
    # 规范混凝土强度等级对应的指标（与表格完全一致）
    spec_data = {
        15: {"f_ck":10.0, "f_tk":1.27, "f_c":7.2, "f_t":0.91, "E_c":22000.0},
        20: {"f_ck":13.4, "f_tk":1.54, "f_c":9.6, "f_t":1.10, "E_c":25500.0},
        25: {"f_ck":16.7, "f_tk":1.78, "f_c":11.9, "f_t":1.27, "E_c":28000.0},
        30: {"f_ck":20.1, "f_tk":2.01, "f_c":14.3, "f_t":1.43, "E_c":30000.0},
        35: {"f_ck":23.4, "f_tk":2.20, "f_c":16.7, "f_t":1.57, "E_c":31500.0},
        40: {"f_ck":26.8, "f_tk":2.39, "f_c":19.1, "f_t":1.71, "E_c":32500.0},
        45: {"f_ck":29.6, "f_tk":2.51, "f_c":21.1, "f_t":1.80, "E_c":33500.0},
        50: {"f_ck":32.4, "f_tk":2.64, "f_c":23.1, "f_t":1.89, "E_c":34500.0},
        55: {"f_ck":35.5, "f_tk":2.74, "f_c":25.3, "f_t":1.96, "E_c":35500.0},
        60: {"f_ck":38.5, "f_tk":2.85, "f_c":27.5, "f_t":2.04, "E_c":36000.0},
        65: {"f_ck":41.5, "f_tk":2.93, "f_c":29.7, "f_t":2.09, "E_c":36500.0},
        70: {"f_ck":44.5, "f_tk":2.99, "f_c":31.8, "f_t":2.14, "E_c":37000.0},
        75: {"f_ck":47.4, "f_tk":3.05, "f_c":33.8, "f_t":2.18, "E_c":37500.0},
        80: {"f_ck":50.2, "f_tk":3.11, "f_c":35.9, "f_t":2.22, "E_c":38000.0}
    }

    # 检查是否为规范强度等级（允许微小误差）
    matched_key = None
    for key in spec_data.keys():
        if abs(f_cuk - key) < 0.1:
            matched_key = key
            break

    if matched_key is not None:
        # 规范值：直接返回表格中的五个核心指标
        spec_vals = spec_data[matched_key]
        return (
            spec_vals["f_tk"],
            spec_vals["f_t"],
            spec_vals["f_ck"],
            spec_vals["f_c"],
            spec_vals["E_c"]
        )

    # 非规范值：执行计算逻辑，返回五个核心指标
    # 计算α_c1（棱柱强度与立方强度的比值）
    alpha_c1 = 0.76 if f_cuk <= 50 else 0.76 + (0.82 - 0.76)/(80 - 50) * (f_cuk - 50)

    # 计算α_c2（脆性折减系数）
    alpha_c2 = 1.00 if f_cuk <= 40 else 1.00 + (0.87 - 1.00)/(80 - 40) * (f_cuk - 40)
    alpha_c2 = max(alpha_c2, 0.1)  # 防止极端值为负

    # 计算δ值
    delta = get_delta(f_cuk)

    # 核心指标计算
    f_ck = 0.88 * alpha_c1 * alpha_c2 * f_cuk
    f_c = f_ck / 1.40
    term = (1 - 1.645 * delta) ** 0.45 if delta is not None else 1.0
    f_tk = 0.88 * 0.395 * (f_cuk ** 0.55) * term * alpha_c2
    f_t = f_tk / 1.40
    E_c = 10 ** 5 / (2.2 + 34.7 / max(f_cuk, 1))  # 避免分母为0

    # 返回保留指定小数位的结果（与原有逻辑一致）
    return (
        round(f_tk, 3),
        round(f_t, 3),
        round(f_ck, 3),
        round(f_c, 3),
        round(E_c, 2)
    )

def calculate_concrete_indices(f_cuk):
    """
    保留原有功能：返回包含提示信息的完整结果字典（用于交互输出）
    参数：f_cuk - 混凝土立方体抗压强度标准值
    返回：包含所有信息的字典
    """
    # 先调用核心函数获取五个指标
    f_tk, f_t, f_ck, f_c, E_c = get_concrete_core_indices(f_cuk)

    # 规范混凝土强度等级对应的f_cuk列表
    spec_keys = [15,20,25,30,35,40,45,50,55,60,65,70,75,80]
    # 判断是否为规范值（允许微小误差）
    is_spec = any(abs(f_cuk - key) < 0.1 for key in spec_keys)
    # 生成提示信息
    if is_spec:
        tips = "该值为规范混凝土强度等级对应的立方体抗压强度，结果与规范表格一致"
        # 匹配规范值的整数（用于显示）
        matched_key = round(f_cuk)
        f_cuk_display = matched_key
    else:
        tips = "提示：该强度值超出规范推荐的C15~C80范围，计算结果仅作参考" if not (15 <= f_cuk <= 80) else ""
        f_cuk_display = round(f_cuk, 1)

    # 整理结果
    return {
        "混凝土强度值f_cuk": f_cuk_display,
        "提示信息": tips,
        "轴心抗拉强度标准值f_tk (N/mm²)": f_tk,
        "轴心抗拉强度设计值f_t (N/mm²)": f_t,
        "轴心抗压强度标准值f_ck (N/mm²)": f_ck,
        "轴心抗压强度设计值f_c (N/mm²)": f_c,
        "弹性模量E_c (N/mm²)": E_c
    }

# 示例调用（保留原有交互功能）
if __name__ == "__main__":
    try:
        f_cuk_input = float(input("请输入混凝土立方体抗压强度标准值（如15、20、80）："))
        # 调用原有函数获取完整结果
        result = calculate_concrete_indices(f_cuk_input)
        print("\n混凝土设计指标计算结果：")
        for key, value in result.items():
            print(f"{key}：{value}")

        # 可选：演示核心函数的返回值
        core_indices = get_concrete_core_indices(f_cuk_input)
        print("\n五个核心设计指标（元组形式）：")
        print(f"f_tk, f_t, f_ck, f_c, E_c = {core_indices}")
    except ValueError:
        print("错误：请输入有效的数字（如15、30、80.5）")

input("按回车键退出...")