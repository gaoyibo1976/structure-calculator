"""矩形截面梁抗弯承载力计算模块
依据：GB 50010-2010
"""
from sympy import sqrt
import concrete #导入concrete模块
import rebar #导入rebar模块


def beam_rect_fc(b, h, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc):
    """
    矩形截面梁抗弯承载力计算
    :param b: 腹板宽度(mm)
    :param h: 梁总高度(mm)
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
    fc, ft, Ec, α1, β1= conc["fc"], conc["ft"], conc["Ec"], conc["α1"], conc["β1"]
    εcu = 0.0033

    rt = rebar.get_params(fy_grade)
    fy, Es, ξb = rt["fy"], rt["Es"], rt["ξb"]

    rc = rebar.get_params(fyc_grade)
    fyc = rc["fy"]

    h0 = h - ast
    x = (fy * Ast - fy * Asc) / (α1 * fc * b)
    xb = ξb * h0
    σs = fy
    σsc = fyc

    # ========== 2. 抗弯承载力计算==========
    if x < 2 * asc:
        Ast1 = α1 * fc * b * 2 * asc / fy
        if Ast <= Ast1:
            x = fy * Ast / (α1 * fc * b)
            σsc = 0
            Mu = α1 * fc * b * x * (h0 - x / 2) / 1e6
        else:
            x = 2 * asc
            σsc = (fy * Ast - α1 * fc * b * x) / Asc
            Mu = α1 * fc * b * 2 * asc * (h0 - asc) / 1e6 + σsc * Asc * (h0 - asc) / 1e6
    elif x > xb:
        a1 = α1 * fc * b
        b1 = fyc * Asc + Es * εcu * Ast
        c1 = -Es * εcu * β1 * h0 * Ast
        x = (-b1 + sqrt(b1 * b1 - 4 * a1 * c1)) / (2 * a1)
        σs = Es * εcu * (β1 * h0 / x - 1)
        Mu = α1 * fc * b * x * (h0 - x / 2) / 1e6 + fyc * Asc * (h0 - asc) / 1e6
    else:
        Mu = α1 * fc * b * x * (h0 - x / 2) / 1e6 + fy * Asc * (h0 - asc) / 1e6

    if σs * Ast - α1 * fc * b * x - σsc * Asc < 0.001:
        check = "✓轴力平衡校验通过!"
    else:
        check = "×轴力平衡校验未通过!"

    # ========== 3. 整理计算结果 ==========
    x = round(x, 1)
    xb = round(xb, 1)
    ξ = round(x / h0,4)
    ξb = round(ξb,4)
    Mu = round(Mu, 2)
    σs = round(σs, 1)
    σsc = round(σsc, 1)

    # ========== 4. 返回结果 ==========
    result = (x,xb,ξ,ξb,Mu,σs,σsc,check)
    return result
