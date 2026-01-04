"""矩形截面梁抗弯承载力计算模块
依据：GB 50010-2010
"""
from typing import Tuple, Dict
from common.utils import solve_quadratic_equation
from common.exceptions import CalculationError, ParameterError, MaterialError, GeometryError
from . import concrete, rebar

# 混凝土极限压应变（规范定值）
εcu: float = 0.0033


def get_material_params(fcuk: float, fy_grade: str, fyc_grade: str) -> Tuple[Tuple[float, float, float, float, float], Tuple[float, float, float], float]:
    """
    获取混凝土和钢筋的材料参数
    :param fcuk: 混凝土立方体抗压强度等级值（如30,40）
    :param fy_grade: 受拉钢筋强度等级（如"HRB400"）
    :param fyc_grade: 受压钢筋强度等级（如"HRB400"）
    :return: tuple - (混凝土参数, 受拉钢筋参数, 受压钢筋参数)
             混凝土参数: (fc, ft, Ec, α1, β1)
             受拉钢筋参数: (fy, Es, ξb)
             受压钢筋参数: fyc
    """
    # 获取混凝土参数
    conc: Dict[str, float] = concrete.get_params(fcuk)
    fc: float = conc["fc"]
    ft: float = conc["ft"]
    Ec: float = conc["Ec"]
    α1: float = conc["α1"]
    β1: float = conc["β1"]
    
    # 获取受拉钢筋参数（动态计算ξb）
    rt: Dict[str, float] = rebar.get_params(fy_grade, fcuk=fcuk)
    fy: float = rt["fy"]
    Es: float = rt["Es"]
    ξb: float = rt["ξb"]
    
    # 获取受压钢筋参数（动态计算ξb）
    rc: Dict[str, float] = rebar.get_params(fyc_grade, fcuk=fcuk)
    fyc: float = rc["fy"]
    
    return (fc, ft, Ec, α1, β1), (fy, Es, ξb), fyc


def calculate_axial_balance_check(σs: float, Ast: float, α1: float, fc: float, b: float, x: float, σsc: float, Asc: float, additional_force: float = 0) -> str:
    """
    轴力平衡校验
    :param σs: 受拉钢筋应力(N/mm²)
    :param Ast: 受拉钢筋面积(mm²)
    :param α1: 混凝土等效矩形应力图形系数
    :param fc: 混凝土轴心抗压强度设计值(N/mm²)
    :param b: 截面宽度(mm)
    :param x: 混凝土受压区高度(mm)
    :param σsc: 受压钢筋应力(N/mm²)
    :param Asc: 受压钢筋面积(mm²)
    :param additional_force: 附加力（用于T形截面的翼缘部分）
    :return: str - 校验结果
    """
    balance: float = σs * Ast - α1 * fc * b * x - σsc * Asc - additional_force
    if abs(balance) < 0.001:
        return "✓轴力平衡校验通过!"
    else:
        return "×轴力平衡校验未通过!"


def beam_rect_fc(b: float, h: float, fcuk: float, fy_grade: str, fyc_grade: str, 
                 Ast: float, ast: float, Asc: float, asc: float, γ0: float) -> Tuple[float, float, float, float, float, float, float, str]:
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
    :param γ0: 结构重要性系数
    :return: tuple - (x, xb, ξ, ξb, Mu, σs, σsc, check)
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
    if b <= 0 or h <= 0:
        raise ParameterError("截面尺寸必须大于0", parameter=f"b={b}, h={h}")
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

    # 计算初始受压区高度
    denominator = α1 * fc * b
    if denominator <= 0:
        raise CalculationError("计算分母为0，无法计算受压区高度", parameter=f"α1={α1}, fc={fc}, b={b}")
    
    x = (fy * Ast - fy * Asc) / denominator
    xb = ξb * h0
    σs = fy
    σsc = fyc

    # ========== 3. 抗弯承载力计算==========
    try:
        if x < 2 * asc:
            Ast1 = α1 * fc * b * 2 * asc / fy
            if Ast <= Ast1:
                x = fy * Ast / denominator
                σsc = 0
                Mu = α1 * fc * b * x * (h0 - x / 2) / 1e6
            else:
                x = 2 * asc
                σsc = (fy * Ast - α1 * fc * b * x) / Asc if Asc > 0 else 0
                Mu = α1 * fc * b * 2 * asc * (h0 - asc) / 1e6 + σsc * Asc * (h0 - asc) / 1e6
        elif x > xb:
            a1 = α1 * fc * b
            b1 = fyc * Asc + Es * εcu * Ast
            c1 = -Es * εcu * β1 * h0 * Ast
            # 使用公共函数解二次方程
            x = solve_quadratic_equation(a1, b1, c1)
            
            if x <= 0:
                raise CalculationError("超筋截面计算失败，受压区高度无效", parameter=f"x={x}")

            σs = Es * εcu * (β1 * h0 / x - 1)
            Mu = α1 * fc * b * x * (h0 - x / 2) / 1e6 + fyc * Asc * (h0 - asc) / 1e6
        else:
            Mu = α1 * fc * b * x * (h0 - x / 2) / 1e6 + fy * Asc * (h0 - asc) / 1e6
    except ZeroDivisionError as e:
        raise CalculationError(f"计算过程中出现除零错误: {str(e)}")
    except Exception as e:
        raise CalculationError(f"抗弯承载力计算失败: {str(e)}")

    # 轴力平衡校验
    check = calculate_axial_balance_check(σs, Ast, α1, fc, b, x, σsc, Asc)

    # 结构重要性系数修正
    Mu = Mu / γ0

    # ========== 4. 整理计算结果 ==========
    x = round(x, 1)
    xb = round(xb, 1)
    ξ = round(x / h0, 4)
    ξb = round(ξb, 4)
    Mu = round(Mu, 1)
    σs = round(σs, 1)
    σsc = round(σsc, 1)

    # ========== 5. 返回结果 ==========
    result = (x, xb, ξ, ξb, Mu, σs, σsc, check)
    return result