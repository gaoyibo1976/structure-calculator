
def report_beam_t_fc(num,param,result):
    b, h, bf, hf, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc = param
    flag,x, xb, ξ, ξb, Mu, σs, σsc,check = result
    report = f"""=====T形截面梁已知配筋计算抗弯承载力=====
{num}
一.输入参数
1.1 梁宽b：{b}mm
1.2 梁高h：{h}mm
1.3 受压翼缘宽度bf'：{bf}mm
1.4 受压翼缘厚度hf'：{hf}mm
1.5 混凝土强度等级：C{fcuk}
1.6 受拉钢筋强度等级：{fy_grade}N/mm²
1.7 受压钢筋强度等级：{fyc_grade}N/mm²
1.8 受拉钢筋面积As：{Ast}mm²
1.9 受拉钢筋面积As'：{Asc}mm²
1.10 受拉钢筋保护计算厚度as：{ast}mm
1.11 受压钢筋保护计算厚度as'：{asc}mm
二.计算结果
2.1 T形截面类型判别：{flag}
2.2 混凝土受压区高度x={x}mm
2.3 界限相对受压区高度ξbh0={xb}mm
2.4 相对受压区高度比ξ={ξ}
2.5 界限相对受压区高度比ξb={ξb}
2.6 抗弯承载力Mu={Mu}kN·m
2.7 受压钢筋应力σs'={σsc:.1f}N/mm²
2.8 受拉钢筋应力σs ={σs:.1f}N/mm²
{check}
"""
    return report
