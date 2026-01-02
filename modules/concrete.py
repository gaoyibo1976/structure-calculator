def get_delta(fcuk):
    """
    根据混凝土立方体抗压强度fcuk，通过线性插值/外推获取变异系数δ（来自表1）
    支持任意数值输入，对极端值采用趋势外推
    """
    # 基础δ值数据（来自表1：fcuk对应强度等级，δ为表中取值）
    delta_data = {
        15: 0.21,   # C15对应fcuk=15，δ=0.21
        20: 0.18,   # C20对应fcuk=20，δ=0.18
        25: 0.16,   # C25对应fcuk=25，δ=0.16
        30: 0.14,   # C30对应fcuk=30，δ=0.14
        35: 0.13,   # C35对应fcuk=35，δ=0.13
        40: 0.12,   # C40对应fcuk=40，δ=0.12
        45: 0.12,   # C45对应fcuk=45，δ=0.12
        50: 0.11,   # C50对应fcuk=50，δ=0.11
        55: 0.11,   # C55对应fcuk=55，δ=0.11
        60: 0.10,   # C60对应fcuk=60，δ=0.10
        65: 0.10,   # C65对应fcuk=65，δ=0.10
        70: 0.10,   # C70对应fcuk=70，δ=0.10
        75: 0.10,   # C75对应fcuk=75，δ=0.10
        80: 0.10    # C80对应fcuk=80，δ=0.10
    }
    sorted_f = sorted(delta_data.keys())  # 排序后的fcuk：[15,20,25,30,35,40,45,50,55,60,65,70,75,80]
    min_f, max_f = sorted_f[0], sorted_f[-1]  # 最小fcuk=15，最大fcuk=80

    # 情况1：fcuk在表1的规范值中，直接返回对应的δ
    if fcuk in delta_data:
        return delta_data[fcuk]

    # 情况2：fcuk小于最小值（15）：按前两个规范点（15→20）的斜率外推
    if fcuk < min_f:
        slope = (delta_data[sorted_f[1]] - delta_data[sorted_f[0]]) / (sorted_f[1] - sorted_f[0])
        delta = delta_data[min_f] + slope * (fcuk - min_f)
        return delta

    # 情况3：fcuk大于最大值（80）：按最后两个规范点（75→80）的斜率外推（二者δ均为0.10，斜率为0）
    if fcuk > max_f:
        slope = (delta_data[sorted_f[-1]] - delta_data[sorted_f[-2]]) / (sorted_f[-1] - sorted_f[-2])
        delta = delta_data[max_f] + slope * (fcuk - max_f)
        return delta

    # 情况4：fcuk在表1的规范值之间，线性插值
    for i in range(len(sorted_f)):
        if sorted_f[i] > fcuk:
            # 找到当前fcuk的上下界规范值
            lower_f, upper_f = sorted_f[i-1], sorted_f[i]
            lower_delta, upper_delta = delta_data[lower_f], delta_data[upper_f]
            # 线性插值公式
            delta = lower_delta + (upper_delta - lower_delta) * (fcuk - lower_f) / (upper_f - lower_f)
            return delta
    return None

def get_concretEcore_indices(fcuk):
    """
    核心函数：返回五个核心设计指标（供其他py文件调用）
    参数：fcuk - 混凝土立方体抗压强度标准值
    返回：元组 (ftk, ft, fck, fc, Ec)
          分别对应：轴心抗拉强度标准值、轴心抗拉强度设计值、
                  轴心抗压强度标准值、轴心抗压强度设计值、弹性模量
    """
    # 规范混凝土强度等级对应的指标（与表格完全一致）
    spec_data = {
        15: {"fck":10.0, "ftk":1.27, "fc":7.2, "ft":0.91, "Ec":22000.0},
        20: {"fck":13.4, "ftk":1.54, "fc":9.6, "ft":1.10, "Ec":25500.0},
        25: {"fck":16.7, "ftk":1.78, "fc":11.9, "ft":1.27, "Ec":28000.0},
        30: {"fck":20.1, "ftk":2.01, "fc":14.3, "ft":1.43, "Ec":30000.0},
        35: {"fck":23.4, "ftk":2.20, "fc":16.7, "ft":1.57, "Ec":31500.0},
        40: {"fck":26.8, "ftk":2.39, "fc":19.1, "ft":1.71, "Ec":32500.0},
        45: {"fck":29.6, "ftk":2.51, "fc":21.1, "ft":1.80, "Ec":33500.0},
        50: {"fck":32.4, "ftk":2.64, "fc":23.1, "ft":1.89, "Ec":34500.0},
        55: {"fck":35.5, "ftk":2.74, "fc":25.3, "ft":1.96, "Ec":35500.0},
        60: {"fck":38.5, "ftk":2.85, "fc":27.5, "ft":2.04, "Ec":36000.0},
        65: {"fck":41.5, "ftk":2.93, "fc":29.7, "ft":2.09, "Ec":36500.0},
        70: {"fck":44.5, "ftk":2.99, "fc":31.8, "ft":2.14, "Ec":37000.0},
        75: {"fck":47.4, "ftk":3.05, "fc":33.8, "ft":2.18, "Ec":37500.0},
        80: {"fck":50.2, "ftk":3.11, "fc":35.9, "ft":2.22, "Ec":38000.0}
    }

    # 检查是否为规范强度等级（允许微小误差）
    matched_key = None
    for key in spec_data.keys():
        if abs(fcuk - key) < 0.1:
            matched_key = key
            break

    if matched_key is not None:
        # 规范值：直接返回表格中的五个核心指标
        spec_vals = spec_data[matched_key]
        return (
            spec_vals["ftk"],
            spec_vals["ft"],
            spec_vals["fck"],
            spec_vals["fc"],
            spec_vals["Ec"]
        )

    # 非规范值：执行计算逻辑，返回五个核心指标
    # 计算α_c1（棱柱强度与立方强度的比值）
    alpha_c1 = 0.76 if fcuk <= 50 else 0.76 + (0.82 - 0.76)/(80 - 50) * (fcuk - 50)

    # 计算α_c2（脆性折减系数）
    alpha_c2 = 1.00 if fcuk <= 40 else 1.00 + (0.87 - 1.00)/(80 - 40) * (fcuk - 40)
    alpha_c2 = max(alpha_c2, 0.1)  # 防止极端值为负

    # 计算δ值
    delta = get_delta(fcuk)

    # 核心指标计算
    fck = 0.88 * alpha_c1 * alpha_c2 * fcuk
    fc = fck / 1.40
    term = (1 - 1.645 * delta) ** 0.45 if delta is not None else 1.0
    ftk = 0.88 * 0.395 * (fcuk ** 0.55) * term * alpha_c2
    ft = ftk / 1.40
    Ec = 10 ** 5 / (2.2 + 34.7 / max(fcuk, 1))  # 避免分母为0

    # 返回保留指定小数位的结果（与原有逻辑一致）
    return (
        round(ftk, 3),
        round(ft, 3),
        round(fck, 3),
        round(fc, 3),
        round(Ec, 2)
    )

def calculatEconcrete_indices(fcuk):
    """
    保留原有功能：返回包含提示信息的完整结果字典（用于交互输出）
    参数：fcuk - 混凝土立方体抗压强度标准值
    返回：包含所有信息的字典
    """
    # 先调用核心函数获取五个指标
    ftk, ft, fck, fc, Ec = get_concretEcore_indices(fcuk)

    # 规范混凝土强度等级对应的fcuk列表
    spec_keys = [15,20,25,30,35,40,45,50,55,60,65,70,75,80]
    # 判断是否为规范值（允许微小误差）
    is_spec = any(abs(fcuk - key) < 0.1 for key in spec_keys)
    # 生成提示信息
    if is_spec:
        tips = "该值为规范混凝土强度等级对应的立方体抗压强度，结果与规范表格一致"
        # 匹配规范值的整数（用于显示）
        matched_key = round(fcuk)
        fcuk_display = matched_key
    else:
        tips = "提示：该强度值超出规范推荐的C15~C80范围，计算结果仅作参考" if not (15 <= fcuk <= 80) else ""
        fcuk_display = round(fcuk, 1)

    # 整理结果
    return {
        "fcuk": fcuk_display,
        "ftk": ftk,
        "ft": ft,
        "fck": fck,
        "fc": fc,
        "Ec": Ec
    }

# 示例调用（保留原有交互功能）
if __name__ == "__main__":
    try:
        fcuk_input = float(input("请输入混凝土立方体抗压强度标准值（如15、20、80）："))
        # 调用原有函数获取完整结果
        result = calculatEconcrete_indices(fcuk_input)
        print("\n混凝土设计指标计算结果：")
        for key, value in result.items():
            print(f"{key}：{value}")
        # 可选：演示核心函数的返回值
        core_indices = get_concretEcore_indices(fcuk_input)
        print("\n五个核心设计指标（元组形式）：")
        print(f"ftk, ft, fck, fc, Ec = {core_indices}")
    except ValueError:
        print("错误：请输入有效的数字（如15、30、80.5）")

