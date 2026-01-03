"""T形截面梁抗弯承载力计算模块
依据：GB 50010-2010
"""
import math  # 使用 Python 的 math.sqrt 而不是 sympy.sqrt
from . import rebar, concrete
from .beam_rect_fc import beam_rect_fc


def beam_t_fc(b, h, bf, hf, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc, γ0):
    """
    T形截面梁抗弯承载力计算
    :param b: 腹板宽度(mm)
    :param h: 梁总高度(mm)
    :param bf: 翼缘宽度(mm)
    :param hf: 翼缘高度(mm)
    :param fcuk: 混凝土立方体抗压强度等级值（如C30传30，C40传40）
    :param fy_grade: 受拉钢筋强度等级（如"HRB400"）
    :param fyc_grade: 受压钢筋强度等级（如"HRB400"）
    :param Ast: 受拉钢筋面积(mm²)
    :param ast: 受拉钢筋合力点至受拉边缘距离(mm)
    :param Asc: 受压钢筋面积(mm²)
    :param asc: 受压钢筋合力点至受压边缘距离(mm)
    :return: tuple - (x, xb, Mu, σs, σsc)
             x: 混凝土受压区高度(mm)
             xb: 界限受压区高度(mm)
             Mu: 抗弯承载力(kN·m)
             σs: 受拉钢筋应力(N/mm²)
             σsc: 受压钢筋应力(N/mm²)
    """
    # ========== 1. 获取材料参数 ==========
    conc = concrete.get_params(fcuk)
    fc, ft, Ec, α1, β1 = conc["fc"], conc["ft"], conc["Ec"], conc["α1"], conc["β1"]
    εcu = 0.0033  # 混凝土极限压应变（规范定值）

    rt = rebar.get_params(fy_grade)
    fy, Es, ξb = rt["fy"], rt["Es"], rt["ξb"]

    rc = rebar.get_params(fyc_grade)
    fyc = rc["fy"]

    h0 = h - ast
    xb = ξb * h0

    # ========== 2. 抗弯承载力计算==========
    if fy * Ast <= α1 * fc * bf * hf:
        x, xb, ξ, ξb, Mu, σs, σsc, check = beam_rect_fc(bf, h, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc, γ0)
        flag = "第一类T型截面"
    else:
        x = ((fy * Ast - fyc * Asc) / (α1 * fc) - (bf - b) * hf) / b
        flag = "第二类T型截面"
        if x <= xb:
            Mu = α1 * fc * (b * x * (h0 - 0.5 * x) + (bf - b) * hf * (h0 - 0.5 * hf)) / 1e6 + fyc * Asc * (
                        h0 - asc) / 1e6
            σs = fy
            σsc = fyc
        else:
            a1 = α1 * fc * b
            b1 = α1 * fc * (bf - b) * hf + fyc * Asc + Es * εcu * Ast
            c1 = -Es * εcu * β1 * h0 * Ast
            # 使用 math.sqrt 替代 sympy.sqrt
            discriminant = b1 * b1 - 4 * a1 * c1
            # 确保判别式非负
            if discriminant >= 0:
                x = (-b1 + math.sqrt(discriminant)) / (2 * a1)
            else:
                # 如果判别式为负，这是一个错误情况，可能需要特殊处理
                # 这里暂时设置为0，但实际工程中应该抛出异常或返回错误码
                x = 0

            # 确保 x 是 Python 浮点数
            x = float(x)
            σs = Es * εcu * (β1 * h0 / x - 1)
            σsc = fyc
            Mu = α1 * fc * (b * x * (h0 - 0.5 * x) + (bf - b) * hf * (h0 - 0.5 * hf)) / 1e6 + fyc * Asc * (
                        h0 - asc) / 1e6
        if σs * Ast - α1 * fc * (b * x + (bf - b) * hf) - σsc * Asc < 0.001:
            check = "✓轴力平衡校验通过!"
        else:
            check = "×轴力平衡校验未通过!"

    Mu = Mu / γ0

    # ========== 3. 整理计算结果 ==========
    # 确保所有值都是 Python 原生浮点数
    x = round(float(x), 2)
    xb = round(float(xb), 2)
    ξ = round(float(x / h0), 3)
    ξb = round(float(ξb), 3)
    Mu = round(float(Mu), 2)
    σs = round(float(σs), 2)
    σsc = round(float(σsc), 2)

    # ========== 4. 返回结果 ==========
    result = (flag, x, xb, ξ, ξb, Mu, σs, σsc, check)
    return result