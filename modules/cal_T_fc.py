"""T形截面梁抗弯承载力计算模块
依据：GB 50010-2010
"""
from sympy import sqrt
import concrete
import rebar
from calc_rect_fc import beam_rect_fc


def beam_T_fc(b, h, bf, hf, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc):
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
    # ========== 1. 精准获取Morgain同款材料参数 ==========
    fc = concrete.get_fc(fcuk)
    α1 = concrete.get_alpha1(fcuk)
    β1 = concrete.get_beta1(fcuk)
    εcu = 0.0033  # 混凝土极限压应变（规范定值）
    Es = rebar.get_Es(fy_grade)
    fy = rebar.get_fy(fy_grade)
    fyc = rebar.get_fyc(fyc_grade)

    # ========== 2. 计算界限参数 ==========
    ξb = β1 / (1 + fy / (Es * εcu))
    h0 = h - ast
    xb = ξb * h0

    # ========== 3. T形截面类型判定==========
    if fy * Ast <= α1 * fc * bf * hf:
        x,xb,Mu,σs,σsc = beam_rect_fc(bf, h, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc)
        flag = "第一类T型截面"
    else:
        x = ((fy * Ast - fyc * Asc) / (α1 * fc) - (bf - b) * hf) / b
        flag = "第二类T型截面"
        if x <= xb:
            Mu = α1 * fc * (b * x *(h0 - 0.5 * x) + (bf - b) * hf * (h0 - 0.5 * hf)) / 1e6 + fyc * Asc * (h0 - asc) / 1e6
            σs = fy
            σsc = fyc
        else:
            σs = Es * εcu * (β1 * h0 / x - 1)
            σsc = fyc
            a1 = α1 * fc * b
            b1 = α1 * fc * (bf - b)* hf + fyc * Asc + Es * εcu * Ast
            c1 = -Es * εcu * β1 * h0 * Ast
            x = (-b1 + sqrt(b1 * b1 - 4 * a1 * c1)) / (2 * a1)
            Mu = α1 * fc * (b * x * (h0 - 0.5 * x) + (bf - b) * hf * (h0 - 0.5 * hf)) / 1e6 + fyc * Asc * (h0 - asc) / 1e6

    # ========== 6. 整理计算结果 ==========
    x = round(x, 1)
    xb = round(xb, 1)
    Mu = round(Mu, 2)
    σs = round(σs, 1)
    σsc = round(σsc, 1)

    # ========== 6. 返回结果 ==========
    result = (flag,x, xb, Mu, σs, σsc)
    return result


# ========== 测试入口 ==========
if __name__ == "__main__":
    # 测试案例1
    print("【测试案例1:第一类T形截面】")
    b = 250
    h = 600
    bf = 800
    hf = 120
    fcuk = 40
    fy_grade = "HRB400"
    fyc_grade = "HRB400"
    Ast = 1520
    ast = 40
    Asc = 603
    asc = 40

    # 调用函数
    flag, x, xb, Mu, σs, σsc = beam_T_fc(b, h, bf, hf, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc)

    # 按指定格式输出
    text = f"""
1. {flag}
2. 相对受压区高度 x = {x}mm
3. 界限受压区高度 xb = {xb}mm
4. 抗弯承载力 Mu = {Mu}kN·m
5. 受拉钢筋应力 σs = {σs}N/mm²
6. 受压钢筋应力 σsc = {σsc}N/mm²
{'=' * 60}"""

    # 打印结果
    print(text)

    # 测试案例2
    print("【测试案例2:第一类T形截面】")
    b = 250
    h = 600
    bf = 800
    hf = 120
    fcuk = 40
    fy_grade = "HRB400"
    fyc_grade = "HRB400"
    Ast = 4000
    ast = 40
    Asc = 804
    asc = 40

    # 调用计算（获取所有返回参数）
    flag, x, xb, Mu, σs, σsc = beam_T_fc(b, h, bf, hf, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc)

    text = f"""
1. {flag}
2. 相对受压区高度 x = {x}mm
3. 界限受压区高度 xb = {xb}mm
4. 抗弯承载力 Mu = {Mu}kN·m
5. 受拉钢筋应力 σs = {σs}N/mm²
6. 受压钢筋应力 σsc = {σsc}N/mm²
{'=' * 60}"""

    # 打印结果
    print(text)

    # 测试案例3
    print("【测试案例3:第二类T形截面】")
    b = 250
    h = 600
    bf = 800
    hf = 120
    fcuk = 40
    fy_grade = "HRB400"
    fyc_grade = "HRB400"
    Ast = 6000
    ast = 40
    Asc = 804
    asc = 40

    # 调用计算（获取所有返回参数）
    flag, x, xb, Mu, σs, σsc = beam_T_fc(b, h, bf, hf, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc)

    text = f"""
1. {flag}
2. 相对受压区高度 x = {x}mm
3. 界限受压区高度 xb = {xb}mm
4. 抗弯承载力 Mu = {Mu}kN·m
5. 受拉钢筋应力 σs = {σs}N/mm²
6. 受压钢筋应力 σsc = {σsc}N/mm²
{'=' * 60}"""
    # 打印结果
    print(text)

    # 测试案例4
    print("【测试案例4:第二类T形截面】")
    b = 250
    h = 600
    bf = 800
    hf = 120
    fcuk = 40
    fy_grade = "HRB400"
    fyc_grade = "HRB400"
    Ast = 9000
    ast = 40
    Asc = 804
    asc = 40

    # 调用计算（获取所有返回参数）
    flag, x, xb, Mu, σs, σsc = beam_T_fc(b, h, bf, hf, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc)

    text = f"""
1. {flag}
2. 相对受压区高度 x = {x}mm
3. 界限受压区高度 xb = {xb}mm
4. 抗弯承载力 Mu = {Mu}kN·m
5. 受拉钢筋应力 σs = {σs}N/mm²
6. 受压钢筋应力 σsc = {σsc}N/mm²
{'=' * 60}"""

    # 打印结果
    print(text)