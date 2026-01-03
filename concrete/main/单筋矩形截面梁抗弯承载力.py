# -*- coding: utf-8 -*-

def gen_param(p, r, M):
    """生成通用计算参数模板"""
    steel_str = " + ".join([f"{n}Φ{d}" for d, n in p['rl']])
    return f"""【计算参数】
1. 截面：b={p['b']}mm，h={p['h']}mm，h0={r['h0']:.2f}mm（h0=h-ast）
2. 配筋：{steel_str}，As={r['As']:.2f}mm²，ast={r['ast']:.2f}mm，a'={p['a2']}mm，2a'={2 * p['a2']:.2f}mm
    {r['ast_desc']}
3. 材料：{p['c']}（fc={p['fc']:.1f}MPa），{p['s']}（fy={p['fy']:.1f}MPa）
4. 荷载：M={M}kN·m"""


def gen_param_over(p, r, M):
    """生成超筋梁计算参数模板"""
    steel_str = " + ".join([f"{n}Φ{d}" for d, n in p['rl']])
    return f"""【计算参数】
1. 截面：b={p['b']}mm，h={p['h']}mm，h0={r['h0']:.2f}mm（h0=h-ast）
2. 配筋：{steel_str}，As={r['As']:.2f}mm²，ast={r['ast']:.2f}mm，a'={p['a2']}mm，2a'={2 * p['a2']:.2f}mm
    {r['ast_desc']}
3. 材料：{p['c']}（fc={p['fc']:.1f}MPa，εcu={p['εcu']:.4f}），{p['s']}（fy={p['fy']:.1f}MPa，Es={p['Es']:.0f}MPa，ξb={p['ξb']:.3f}）
4. 荷载：M={M}kN·m"""

def gen_report1(p, r, M, x_calc):
    """生成少筋梁（x<2a'）计算书"""
    res, fp, fe = calc_formula("fy*As*(h0-a2)/1e6", {"fy": p['fy'], "As": r['As'], "h0": r['h0'], "a2": p['a2']})
    r['Mu'] = res
    basic_template = gen_param(p, r, M)
    return f"""{'=' * 80}
钢筋混凝土梁受弯计算书（工况1：x<2a'）
计算依据：GB 50010-2010 第6.2.10条
{'=' * 80}
{basic_template}
【钢筋屈服判定】
{x_calc}
2. 判定条件：
    x={r['x']:.2f}mm < 2a'={2 * p['a2']:.2f}mm → 受压筋未屈服
【三、承载力计算】
公式：{fp}
代入：{fe}
结果：Mu={r['Mu']:.2f}kN·m
【四、配筋率验算】
ρmin={r['ρmin']:.4f}，ρ={r['ρ']:.4f} → 满足
【五、结论】
承载力{'满足' if r['Mu'] >= M else '不满足'}，建议增加受压筋面积
{'=' * 80}"""


def gen_report2(p, r, M, x_calc):
    """生成适筋梁计算书"""
    res, fp_xi, fe_xi = calc_formula("x/h0", {"x": r['x'], "h0": r['h0']})
    r['ξ'] = res
    res, fp_Mu, fe_Mu = calc_formula(
        "(α1*fc*b*x*(h0-x/2))/1e6",
        {"α1": p['α1'], "fc": p['fc'], "b": p['b'], "x": r['x'], "h0": r['h0']}
    )
    r['Mu'] = res
    basic_template = gen_param(p, r, M)
    return f"""{'=' * 80}
钢筋混凝土梁受弯计算书（工况2：适筋梁）
计算依据：GB 50010-2010 第6.2.6条
{'=' * 80}
{basic_template}
【钢筋屈服判定】
{x_calc}
{r['ξbh0_calc']}
3. 判定条件：
    2a'={2 * p['a2']:.2f} ≤ x={r['x']:.2f} ≤ ξb·h0={r['ξbh0']:.2f}mm → 受拉钢筋屈服，适筋梁
【三、承载力计算】
1. 相对受压区高度：
公式：{fp_xi}
代入：{fe_xi}
结果：ξ={r['ξ']:.4f}
2. 受弯承载力：
公式：{fp_Mu}
代入：{fe_Mu}
结果：Mu={r['Mu']:.2f}kN·m
【四、配筋率验算】
ρmin={r['ρmin']:.4f}，ρ={r['ρ']:.4f} → 满足
【五、结论】
适筋梁，延性破坏，承载力{'满足' if r['Mu'] >= M else '不满足'}
{'=' * 80}"""


def gen_report3(p, r, M, x_calc):
    """生成超筋梁计算书"""
    r['A'] = p['α1'] * p['fc'] * p['b']
    r['B'] = p['Es'] * p['εcu'] * r['As']
    r['C'] = -p['Es'] * p['εcu'] * r['As'] * r['h0']
    delta = r['B'] ** 2 - 4 * r['A'] * r['C']
    r['xa'] = (-r['B'] + math.sqrt(delta)) / (2 * r['A'])
    r['xf'] = r['xa'] if r['xa'] <= p['h'] else p['h']
    r['σs'] = p['Es'] * p['εcu'] * (r['h0'] - r['xf']) / r['xf']
    res, fp_Mu, fe_Mu = calc_formula(
        "(α1*fc*b*xf*(h0-xf/2))/1e6",
        {"α1": p['α1'], "fc": p['fc'], "b": p['b'], "xf": r['xf'], "h0": r['h0']}
    )
    r['Mu'] = res
    r['sg'] = "4Φ22（As=1520mm²）" if p['s'] == "HRB400" else "3Φ22（As=1140mm²）"
    basic_template = gen_param_over(p, r, M)
    return f"""{'=' * 80}
钢筋混凝土梁受弯计算书（工况3：超筋梁）
计算依据：GB 50010-2010 第6.2.1条
{'=' * 80}
{basic_template}
【钢筋屈服判定】
{x_calc}
{r['ξbh0_calc']}
3. 判定条件：
    x={r['x']:.2f}mm > ξb·h0={r['ξbh0']:.2f}mm → 受拉钢筋未屈服，超筋梁（简化公式失效）
【三、精准计算（平截面假定）】
1. 方程：α1·fc·b·x² + Es·εcu·As·x - Es·εcu·As·h0 = 0
2. 系数：A={r['A']:.0f}，B={r['B']:.0f}，C={r['C']:.0f}
3. 求解：x={r['xa']:.2f}mm → 修正x={r['xf']:.2f}mm（x≤h）
4. 钢筋应力：σs={r['σs']:.2f}MPa < fy={p['fy']:.1f}MPa（未屈服）
5. 极限承载力：
公式：{fp_Mu}
代入：{fe_Mu}
结果：Mu={r['Mu']:.2f}kN·m
【四、配筋率验算】
ρmin={r['ρmin']:.4f}，ρ={r['ρ']:.4f} → 满足
【五、结论】
超筋梁，脆性破坏，规范禁止！
整改建议：{r['sg']}
{'=' * 80}"""

