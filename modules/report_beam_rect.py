
def report_beam_rect_fc(num,param,result):
    b, h, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc = param
    x, xb, ξ, ξb, Mu, σs, σsc, check = result
    report = f"""=====矩形截面梁已知配筋计算抗弯承载力=====
{num}
一.输入参数
1.1 梁宽b：{b}mm
1.2 梁高h：{h}mm
1.3 混凝土强度等级：C{fcuk}
1.4 受拉钢筋强度等级：{fy_grade}N/mm²
1.5 受压钢筋强度等级：{fyc_grade}N/mm²
1.6 受拉钢筋面积As：{Ast}mm²
1.7 受拉钢筋面积As'：{Asc}mm²
1.8 受拉钢筋保护计算厚度as：{ast}mm
1.9 受压钢筋保护计算厚度as'：{asc}mm
二.计算结果
2.1 混凝土受压区高度x={x}mm
2.2 界限相对受压区高度ξbh0={xb}mm
2.3 相对受压区高度比ξ={ξ}
2.4 界限相对受压区高度比ξb={ξb}
2.5 抗弯承载力Mu={Mu}kN·m
2.6 受压钢筋应力σs'={σsc:.1f}N/mm²
2.7 受拉钢筋应力σs ={σs:.1f}N/mm²
{check}"""
    return report
