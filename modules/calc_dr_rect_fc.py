#双筋矩形截面梁抗弯承载力计算函数
import concrete #导入concrete模块
import rebar #导入rebar模块

def beam_dr_rect_fc(b, h, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc):
    ftk, ft, fck, fc, Ec = concrete.get_concretEcore_indices(fcuk)
    fy, ξb, Es = rebar.get_rebar(fy_grade)
    fyc = rebar.get_rebar(fyc_grade)[0]
    α1 = 1.0
    h0 = h - ast
    ρmin = max(0.002, 0.45 * ft / fy)
    ρ = Ast / (b * h)
    x = (fy * Ast - fy * Asc) / (α1 * fc * b)
    if x < 2 * asc:
        Ast1 = α1 * fc * 2 * asc / fy
        if Ast <= Ast1:
            x = fy * Ast / (α1 * fc * b)
            Mu = α1 * fc * b * x * (h0 - x / 2) / 1e6
        else:
            σsc = (α1 * fc * b * 2 * asc - fy * Asc) / Asc
            Mu = α1 * fc * b * 2 * asc * (h0 - asc) / 1e6 + σsc * Asc * (h0 - asc)
    elif x > ξb * h0:
        Mu = α1 * fc * b * ξb * h0 * (h0 - ξb * h0 / 2) / 1e6 + fy * Asc * (h0 - asc) / 1e6
       # σs = Es * εcu * (β1)
    else:
        Mu = α1 * fc * b * x * (h0 - x / 2) / 1e6 + fy * Asc * (h0 - asc) / 1e6

    return Mu


if __name__ == "__main__":
    b, h, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc = 300, 600, 30, "HRB400", "HRB400", 2500, 42.5, 1000,42.5
    Mu = beam_dr_rect_fc(b, h, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc)
    print(f"抗弯承载力Mu={Mu:.2f}kN·m")
