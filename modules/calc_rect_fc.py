#双筋矩形截面梁抗弯承载力计算函数
from sympy import sqrt

import concrete #导入concrete模块
import rebar #导入rebar模块


def beam_rect_fc(b, h, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc):

    conc = concrete.get_params(fcuk)
    fc, ft, Ec, β1= conc["fc"], conc["ft"], conc["Ec"], conc["β1"]
    εcu = 0.0033

    rt = rebar.get_params(fy_grade)
    fy, Es, ξb = rt["fy"], rt["Es"], rt["ξb"]

    fyc = rebar.get_params(fyc_grade)["fy"]

    h0 = h - ast
    α1 = 1.0
    x = (fy * Ast - fy * Asc) / (α1 * fc * b)

    if x < 2 * asc:
        Ast1 = α1 * fc * b * 2 * asc / fy
        if Ast <= Ast1:
            x = fy * Ast / (α1 * fc * b)
            Mu = α1 * fc * b * x * (h0 - x / 2) / 1e6
        else:
            x = 2 * asc
            σsc = (α1 * fc * b * x - fy * Asc) / Asc
            Mu = α1 * fc * b * 2 * asc * (h0 - asc) / 1e6 + σsc * Asc * (h0 - asc) / 1e6
    elif x > ξb * h0:
        σs = Es * εcu * (β1 * h0 / x - 1)
        a1 = α1 * fc * b
        b1 = fyc * Asc + Es * εcu * Ast
        c1 = -Es * εcu * β1 * h0 * Ast
        x = (-b1 + sqrt(b1 * b1 - 4 * a1 * c1)) / (2 * a1)
        Mu = α1 * fc * b * x * (h0 - x / 2) / 1e6 + fyc * Asc * (h0 - asc) / 1e6
    else:
        Mu = α1 * fc * b * x * (h0 - x / 2) / 1e6 + fy * Asc * (h0 - asc) / 1e6

    result = (x,Mu)
    return result


if __name__ == "__main__":
    b, h, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc = 300, 600, 30, "HRB400", "HRB400", 900, 42.5, 1000,42.5
    result = beam_rect_fc(b, h, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc)
    x = round(result[0],1)
    Mu = round(result[1],1)
    print(f"混凝土受压区高度x={x}\n抗弯承载力Mu={Mu}kN·m")
