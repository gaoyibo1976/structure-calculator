"""混凝土设计指标模块（解耦版：修正α1/β1逻辑，匹配规范）
"""

# ====================== 1. 导入外部工具函数 ======================
from utils import linear_interp  # 导入独立工具模块的线性插值函数

# ====================== 2. 基础数据（字典名不变） ======================
# 规范等级fc/ft/Ec字典（仅存这三个，正截面α1/β1公式算）
CONC_BASE = {
    15: {"fc": 7.2, "ft": 0.91, "Ec": 22000},
    20: {"fc": 9.6, "ft": 1.10, "Ec": 25500},
    25: {"fc": 11.9, "ft": 1.27, "Ec": 28000},
    30: {"fc": 14.3, "ft": 1.43, "Ec": 30000},
    35: {"fc": 16.7, "ft": 1.57, "Ec": 31500},
    40: {"fc": 19.1, "ft": 1.71, "Ec": 32500},
    45: {"fc": 21.1, "ft": 1.80, "Ec": 33500},
    50: {"fc": 23.1, "ft": 1.89, "Ec": 34500},
    55: {"fc": 25.3, "ft": 1.96, "Ec": 35500},
    60: {"fc": 27.5, "ft": 2.04, "Ec": 36000},
    65: {"fc": 29.7, "ft": 2.09, "Ec": 36500},
    70: {"fc": 31.8, "ft": 2.14, "Ec": 37000},
    75: {"fc": 33.8, "ft": 2.18, "Ec": 37500},
    80: {"fc": 35.9, "ft": 2.22, "Ec": 38000},
}

# 规范等级变异系数δ字典
CONC_DELTA = {
    15: 0.21, 20: 0.18, 25: 0.16, 30: 0.14, 35: 0.13, 40: 0.12,
    45: 0.11, 50: 0.10, 55: 0.09, 60: 0.08, 65: 0.07, 70: 0.07,
    75: 0.07, 80: 0.07
}

# 混凝土分项系数
γc = 1.4


# ====================== 3. 辅助计算函数 ======================
# 3.1 获取变异系数δ（调用外部工具模块的线性插值函数）
def _get_delta(fcuk):
    std_g = sorted(CONC_DELTA.keys())
    # 规范等级直接返回
    if fcuk in CONC_DELTA:
        return CONC_DELTA[fcuk]
    # 逐个比较找邻居
    low_g, up_g = None, None
    for g in std_g:
        if g < fcuk:
            low_g = g
        elif g > fcuk:
            up_g = g
            break
    # 调用外部工具模块的线性插值函数
    return linear_interp(fcuk, low_g, up_g, CONC_DELTA[low_g], CONC_DELTA[up_g])


# 3.2 棱柱体系数αc1（内部计算fc用，不对外输出）
def _calc_ac1(fcuk):
    # 原_calc_a1，重命名为αc1避免混淆
    return 0.76 if fcuk <= 50 else 0.76 - (fcuk - 50) * 0.06 / 30


# 3.3 脆性折减系数α2
def _calc_a2(fcuk):
    return 1.0 if fcuk <= 40 else 1.0 - (fcuk - 40) * 0.13 / 40


# 3.4 非标等级fc/ft计算（标准差逻辑）
def _calc_fc_ft(fcuk):
    δ = _get_delta(fcuk)
    ac1 = _calc_ac1(fcuk)  # 用棱柱体系数αc1（内部用）
    a2 = _calc_a2(fcuk)
    # 抗压
    fck = 0.88 * ac1 * a2 * fcuk
    fc = round(fck / γc, 2)
    # 抗拉（标准差核心）
    ftk = 0.395 * (fcuk ** 0.55) * ((1 - 1.645 * δ) ** 0.45)
    ft = round(ftk / γc, 3)
    return fc, ft


# 3.5 非标等级Ec计算
def _calc_Ec(fcuk):
    return round(10 ** 5 / (2.2 + 34.7 / fcuk), 0)


# 3.6 正截面计算的α1/β1（按规范线性插值，对外输出）
def _calc_alpha_beta(fcuk):
    """按规范计算正截面等效矩形应力图的α1、β1"""
    if fcuk <= 50:
        α1 = 1.0
        β1 = 0.8
    elif fcuk >= 80:
        α1 = 0.94
        β1 = 0.74
    else:
        # C50~C80线性内插（规范要求）
        delta = fcuk - 50
        α1 = 1.0 - delta * (1.0 - 0.94) / (80 - 50)  # 1.0→0.94（跨度30）
        β1 = 0.8 - delta * (0.8 - 0.74) / (80 - 50)    # 0.8→0.74（跨度30）
    # 保留2位小数，符合工程精度
    return round(α1, 2), round(β1, 2)


# ====================== 4. 核心函数 ======================
def get_params(grade):
    """
    核心入口：规范等级查字典，非标等级公式算
    :param grade: 数字类型等级（如30/37/52）
    :return: 完整参数字典（含正截面α1、β1）
    """
    # 类型校验
    if not isinstance(grade, (int, float)):
        raise TypeError("仅支持数字输入（如30/37.5）")
    # 范围校验
    if not (15 <= grade <= 80):
        raise ValueError("等级需为15~80")

    # 规范等级：查字典 + 正截面α1/β1公式算
    if grade in CONC_BASE:
        params = CONC_BASE[grade].copy()
        params["α1"], params["β1"] = _calc_alpha_beta(grade)  # 调用正截面α1/β1计算
        return params

    # 非标等级：全公式算
    fc, ft = _calc_fc_ft(grade)
    Ec = _calc_Ec(grade)
    α1, β1 = _calc_alpha_beta(grade)  # 调用正截面α1/β1计算
    return {"fc": fc, "ft": ft, "Ec": Ec, "α1": α1, "β1": β1}


# ====================== 5. 快捷函数 ======================
def get_fc(grade):
    return get_params(grade)["fc"]


def get_ft(grade):
    return get_params(grade)["ft"]


def get_alpha1(grade):
    return get_params(grade)["α1"]


def get_beta1(grade):
    return get_params(grade)["β1"]


def get_Ec(grade):
    return get_params(grade)["Ec"]


# ====================== 测试示例 ======================
if __name__ == "__main__":
    # 规范等级C30（查字典，正截面α1=1.0、β1=0.8）
    print("C30参数：", get_params(30))
    # 规范等级C55（正截面α1=0.99、β1=0.79）
    print("C55参数：", get_params(55))
    # 非标等级C37（公式算，正截面α1=1.0、β1=0.8）
    print("C37参数：", get_params(37))
    # 快捷函数调用（C80的α1=0.94、β1=0.74）
    print("C80的α1：", get_alpha1(80))
    print("C80的β1：", get_beta1(80))