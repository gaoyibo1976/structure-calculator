from . import rebar,concrete

def report_beam_rect_fc(num,param,result):
    b, h, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc, γ0 = param
    x, xb, ξ, ξb, Mu, σs, σsc, check = result

    conc = concrete.get_params(fcuk)
    fc, ft, Ec, α1, β1= conc["fc"], conc["ft"], conc["Ec"], conc["α1"], conc["β1"]
    εcu = 0.0033

    rt = rebar.get_params(fy_grade)
    fy, Es, ξb = rt["fy"], rt["Es"], rt["ξb"]

    rc = rebar.get_params(fyc_grade)
    fyc = rc["fy"]

    report = f"""=====矩形截面梁已知配筋计算抗弯承载力=====
{num}
一.输入参数
1.1 梁宽b：{b}mm
1.2 梁高h：{h}mm
1.3 混凝土:强度等级C{fcuk}，抗压强度设计值fc={fc:.1f}N/mm²
1.4 受拉钢筋：强度等级{fy_grade}，屈服强度设计值fy={fy:.1f}N/mm²，弹性模量Es={Es:.1f}N/mm²
1.5 受压钢筋：强度等级{fyc_grade}，屈服强度设计值fy'={fyc:.1f}N/mm²
1.6 受拉钢筋面积As：{Ast}mm²
1.7 受拉钢筋面积As'：{Asc}mm²
1.8 受拉钢筋保护计算厚度as：{ast}mm
1.9 受压钢筋保护计算厚度as'：{asc}mm
1.10 结构重要性系数γ0：{γ0:.1f}
二.计算结果
2.1 混凝土受压区高度x={x}mm
2.2 界限相对受压区高度ξb·h0={xb}mm
2.3 相对受压区高度比ξ={ξ}
2.4 界限相对受压区高度比ξb={ξb:.4f}
2.5 非地震作用抗弯承载力Mu={Mu}kN·m
2.6 地震作用时抗弯承载力MuE={Mu / 0.75:.2f}kN·m
2.6 受压钢筋应力σs'={σsc:.1f}N/mm²
2.7 受拉钢筋应力σs ={σs:.1f}N/mm²
{check}
"""
    return report
