"""T形截面梁抗弯承载力计算模块
依据：GB 50010-2010
"""
from typing import Tuple
from common.utils import solve_quadratic_equation
from common.exceptions import CalculationError, ParameterError, MaterialError, GeometryError
from .beam_rect_fc import (
    beam_rect_fc,
    get_material_params,
    calculate_axial_balance_check
)

# 混凝土极限压应变（规范定值）
εcu: float = 0.0033


def beam_t_fc(b: float, h: float, bf: float, hf: float, fcuk: float, fy_grade: str, 
              fyc_grade: str, Ast: float, ast: float, Asc: float, asc: float, γ0: float) -> Tuple[str, float, float, float, float, float, float, float, str]:
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
    :param γ0: 结构重要性系数
    :return: tuple - (flag, x, xb, ξ, ξb, Mu, σs, σsc, check)
             flag: 截面类型（"第一类T型截面"或"第二类T型截面"）
             x: 混凝土受压区高度(mm)
             xb: 界限受压区高度(mm)
             ξ: 相对受压区高度
             ξb: 界限相对受压区高度
             Mu: 抗弯承载力(kN·m)
             σs: 受拉钢筋应力(N/mm²)
             σsc: 受压钢筋应力(N/mm²)
             check: 轴力平衡校验结果
    :raises CalculationError: 计算错误时抛出异常
    :raises ParameterError: 参数错误时抛出异常
    :raises MaterialError: 材料参数错误时抛出异常
    :raises GeometryError: 几何参数错误时抛出异常
    """
    # ========== 1. 参数校验 ==========
    if b <= 0 or h <= 0 or bf <= 0 or hf <= 0:
        raise ParameterError("截面尺寸必须大于0", parameter=f"b={b}, h={h}, bf={bf}, hf={hf}")
    if bf < b:
        raise ParameterError("翼缘宽度必须大于等于腹板宽度", parameter=f"bf={bf}, b={b}")
    if hf >= h:
        raise ParameterError("翼缘高度必须小于梁总高度", parameter=f"hf={hf}, h={h}")
    if Ast < 0 or Asc < 0:
        raise ParameterError("钢筋面积不能为负", parameter=f"Ast={Ast}, Asc={Asc}")
    if ast <= 0 or asc <= 0:
        raise ParameterError("钢筋合力点至边缘距离必须大于0", parameter=f"ast={ast}, asc={asc}")
    if γ0 <= 0:
        raise ParameterError("结构重要性系数必须大于0", parameter=f"γ0={γ0}")

    # ========== 2. 获取材料参数 ==========
    try:
        (fc, ft, Ec, α1, β1), (fy, Es, ξb), fyc = get_material_params(fcuk, fy_grade, fyc_grade)
    except Exception as e:
        raise MaterialError(f"获取材料参数失败: {str(e)}", parameter=f"fcuk={fcuk}, fy_grade={fy_grade}, fyc_grade={fyc_grade}")

    h0 = h - ast
    if h0 <= 0:
        raise GeometryError("有效高度必须大于0", parameter=f"h={h}, ast={ast}, h0={h0}")

    xb = ξb * h0

    # ========== 3. 抗弯承载力计算==========
    try:
        if fy * Ast <= α1 * fc * bf * hf:
            # 第一类T型截面，按宽度为bf的矩形截面计算
            x, xb, ξ, ξb, Mu, σs, σsc, check = beam_rect_fc(bf, h, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc, γ0)
            flag = "第一类T型截面"
        else:
            # 第二类T型截面
            flag = "第二类T型截面"
            denominator = α1 * fc
            if denominator <= 0:
                raise CalculationError("计算分母为0，无法计算受压区高度", parameter=f"α1={α1}, fc={fc}")
            
            x = ((fy * Ast - fyc * Asc) / denominator - (bf - b) * hf) / b
            
            if x <= xb:
                # 适筋截面
                Mu = α1 * fc * (b * x * (h0 - 0.5 * x) + (bf - b) * hf * (h0 - 0.5 * hf)) / 1e6 + fyc * Asc * (h0 - asc) / 1e6
                σs = fy
                σsc = fyc
            else:
                # 超筋截面，需迭代计算
                a1 = α1 * fc * b
                b1 = α1 * fc * (bf - b) * hf + fyc * Asc + Es * εcu * Ast
                c1 = -Es * εcu * β1 * h0 * Ast
                
                # 使用公共函数解二次方程
                x = solve_quadratic_equation(a1, b1, c1)
                
                if x <= 0:
                    raise CalculationError("超筋截面计算失败，受压区高度无效", parameter=f"x={x}")
                
                σs = Es * εcu * (β1 * h0 / x - 1)
                σsc = fyc
                Mu = α1 * fc * (b * x * (h0 - 0.5 * x) + (bf - b) * hf * (h0 - 0.5 * hf)) / 1e6 + fyc * Asc * (h0 - asc) / 1e6
            
            # 轴力平衡校验，考虑翼缘部分的附加力
            additional_force = α1 * fc * (bf - b) * hf
            check = calculate_axial_balance_check(σs, Ast, α1, fc, b, x, σsc, Asc, additional_force)
    except ZeroDivisionError as e:
        raise CalculationError(f"计算过程中出现除零错误: {str(e)}")
    except Exception as e:
        raise CalculationError(f"抗弯承载力计算失败: {str(e)}")

    # 结构重要性系数修正
    Mu = Mu / γ0

    # ========== 4. 整理计算结果 ==========
    # 确保所有值都是 Python 原生浮点数
    x = round(float(x), 2)
    xb = round(float(xb), 2)
    ξ = round(float(x / h0), 3)
    ξb = round(float(ξb), 3)
    Mu = round(float(Mu), 2)
    σs = round(float(σs), 2)
    σsc = round(float(σsc), 2)

    # ========== 5. 返回结果 ==========
    result = (flag, x, xb, ξ, ξb, Mu, σs, σsc, check)
    return result