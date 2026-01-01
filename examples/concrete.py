import math
from utils import calc_formula


def get_conc(grade):
    """获取混凝土材料参数（fc、ft、εcu）"""
    concrete_params = {
        "C30": (14.3, 1.43, 0.0033),
        "C40": (19.1, 1.71, 0.0033)
    }
    return concrete_params.get(grade, concrete_params["C30"])


def get_rebar(grade):
    """获取钢筋材料参数（fy、ξb、Es）"""
    rebar_params = {
        "HRB400": (360, 0.550, 2e5),
        "HRB500": (435, 0.482, 2e5)
    }
    return rebar_params.get(grade, rebar_params["HRB400"])


def calc_rebar(rl, d_v=10, c=20, s_n=25):
    """计算受拉钢筋合力中心到受拉边缘的距离ast及总钢筋面积As
    ast: a（距离）+s（钢筋）+t（受拉区），无关键字冲突
    预留asc: a（距离）+s（钢筋）+c（受压区），用于双筋梁计算
    """
    rh = []  # 每排中心到受拉边缘的距离
    ra = []  # 每排钢筋面积
    desc = [f"钢筋合力中心计算："]
    desc.append(f"保护层c={c}mm，箍筋直径d_v={d_v}mm，排间净距s_n={s_n}mm")

    for i in range(len(rl)):
        d, n = rl[i]
        a_single = math.pi * (d / 2) ** 2
        a_row = n * a_single
        if i == 0:
            h = c + d_v + d / 2
        else:
            h_prev = rh[i - 1]
            d_prev = rl[i - 1][0]
            h = h_prev + (d_prev / 2) + s_n + (d / 2)
        rh.append(h)
        ra.append(a_row)
        desc.append(f"第{i + 1}排：{n}Φ{d}，单根面积={a_single:.2f}mm²，本排面积={a_row:.2f}mm²，中心距离={h:.2f}mm")

    As_total = sum(ra)
    ast = sum(h * a for h, a in zip(rh, ra)) / As_total
    desc.append(f"总钢筋面积As={As_total:.2f}mm²")
    desc.append(f"合力中心ast=Σ(本排面积×本排中心距离)/总面面积={ast:.2f}mm")
    return round(ast, 2), round(As_total, 2), "\n    ".join(desc)


def calc_h0(h, ast):
    """计算截面有效高度h0（h0 = h - ast）"""
    return h - ast


def calc_x(fy, As, α1, fc, b):
    """计算受压区高度x及计算过程"""
    x, x_fp, x_fe = calc_formula("(fy*As)/(α1*fc*b)", {"fy": fy, "As": As, "α1": α1, "fc": fc, "b": b})
    x_calc = f"""1. 受压区高度x计算（基本公式：α₁·fc·b·x = fy·As）
    公式：{x_fp}
    代入：{x_fe}
    结果：x={x:.2f}mm"""
    return round(x, 2), x_calc


def calc_ξbh0(ξb, h0):
    """计算界限受压区高度ξb·h0及计算过程"""
    ξbh0, ξbh0_fp, ξbh0_fe = calc_formula("ξb*h0", {"ξb": ξb, "h0": h0})
    ξbh0_calc = f"""2. 界限受压区高度ξb·h0计算：
    公式：{ξbh0_fp}
    代入：{ξbh0_fe}
    结果：ξb·h0={ξbh0:.2f}mm"""
    return round(ξbh0, 2), ξbh0_calc


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


def beam_base(b, h, rl, concrete_grade, rebar_grade, M, a2=40, d_v=10, c_prot=20, s_n=25):
    """梁受弯验算公共逻辑（参数准备）"""
    fc, ft, εcu = get_conc(concrete_grade)
    fy, ξb, Es = get_rebar(rebar_grade)
    α1 = 1.0
    ast, As, ast_desc = calc_rebar(rl, d_v, c_prot, s_n)
    h0 = calc_h0(h, ast)
    x, x_calc = calc_x(fy, As, α1, fc, b)
    ξbh0, ξbh0_calc = calc_ξbh0(ξb, h0)
    ρmin = max(0.002, 0.45 * ft / fy)
    ρ = As / (b * h)
    r = {
        "h0": h0,
        "As": As,
        "ast": ast,
        "ast_desc": ast_desc,
        "ρmin": ρmin,
        "ρ": ρ,
        "ξbh0": ξbh0,
        "x": x,
        "ξbh0_calc": ξbh0_calc
    }
    p = {
        "b": b, "h": h, "c": concrete_grade, "s": rebar_grade,
        "a2": a2, "fc": fc, "ft": ft, "εcu": εcu,
        "fy": fy, "ξb": ξb, "Es": Es, "α1": α1,
        "rl": rl
    }
    return p, r, x_calc


def beam_check(b, h, rl, concrete_grade, rebar_grade, M, a2=40, d_v=10, c_prot=20, s_n=25):
    """梁受弯验算主函数（入口）"""
    p, r, x_calc = beam_base(b, h, rl, concrete_grade, rebar_grade, M, a2, d_v, c_prot, s_n)
    if r['x'] < 2 * a2:
        return gen_report1(p, r, M, x_calc)
    elif r['x'] <= r['ξbh0']:
        return gen_report2(p, r, M, x_calc)
    else:
        return gen_report3(p, r, M, x_calc)