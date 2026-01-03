import re
import math

# 极简变量名：n(根数), d(直径), c(保护层), dv(箍筋直径), sn(排间净距)
# At(总面积), xc(合力中心), rc(各排中心高度), π(圆周率)
π = math.pi


# ---------------------- 梁顶钢筋顺序反转模块 ----------------------
def reverse_top_rebar(r):
    """
    梁顶钢筋顺序反转函数（梁顶标注左近右远→反转为左远右近，匹配梁底计算逻辑）
    :param r: 原平法标注排配置列表（parse_flat输出）
    :return: 反转后的排配置列表
    """
    return r[::-1]


# ---------------------- 平法标注解析模块 ----------------------
def parse_flat(r_str):
    """解析平法标注，返回排配置列表（平法原始顺序，最多四排）"""
    r = []
    if "/" in r_str and " " not in r_str:
        for s in r_str.split("/")[:4]:
            g = re.findall(r"(\d+)d(\d+)", s)
            if g:
                n, d = int(g[0][0]), int(g[0][1])
                r.append((n, d))
    elif " " in r_str:
        s1, s2 = r_str.strip().split(maxsplit=1)
        g = re.findall(r"(\d+)d(\d+)", s1)
        if g:
            tn, d = int(g[0][0]), int(g[0][1])
            for n in list(map(int, s2.split("/")))[:4]:
                r.append((n, d))
    else:
        g = re.findall(r"(\d+)d(\d+)", r_str)
        if g:
            tn = sum(int(n) for n, d in g)
            md = max(int(d) for n, d in g)
            r.append((tn, md))
    return r[:4]


# ---------------------- 核心计算模块（左远右近逻辑） ----------------------
def calc_core(r, c=20, dv=10, sn=25):
    """
    核心计算模块（梁底标注左远右近；梁顶反序后也为左远右近）
    :param r: 排配置列表（parse_flat输出或reverse_top_rebar反转后）
    :param c: 保护层厚度
    :param dv: 箍筋直径
    :param sn: 排间净距
    :return: 计算结果字典
    """
    k = len(r)
    # 反转排序列表：将左远右近转为计算用的左近右远（方便从靠近梁边开始计算高度）
    r_calc = r[::-1]
    n1, d1 = r_calc[0] if k >= 1 else (0, 0)
    n2, d2 = r_calc[1] if k >= 2 else (0, 0)
    n3, d3 = r_calc[2] if k >= 3 else (0, 0)
    n4, d4 = r_calc[3] if k >= 4 else (0, 0)

    # 精度控制：面积1位，距离2位
    prec_A = 1
    prec_x = 2

    # 逐排计算中心高度：从靠近梁边（第1排）到最远（第k排）
    rc_list = [0.0] * k
    height_calc = []
    if k >= 1:
        rc_list[0] = c + dv + d1 / 2
        height_calc.append(f"距离梁边第1排（靠近梁边）：c + dv + d/2 = {c} + {dv} + {d1}/2 = {rc_list[0]:.2f}mm")
    if k >= 2:
        rc_list[1] = rc_list[0] + d1 / 2 + sn + d2 / 2
        height_calc.append(
            f"距离梁边第2排：距离梁边第1排中心 + d1/2 + sn + d2/2 = {rc_list[0]:.2f} + {d1}/2 + {sn} + {d2}/2 = {rc_list[1]:.2f}mm")
    if k >= 3:
        rc_list[2] = rc_list[1] + d2 / 2 + sn + d3 / 2
        height_calc.append(
            f"距离梁边第3排：距离梁边第2排中心 + d2/2 + sn + d3/2 = {rc_list[1]:.2f} + {d2}/2 + {sn} + {d3}/2 = {rc_list[2]:.2f}mm")
    if k >= 4:
        rc_list[3] = rc_list[2] + d3 / 2 + sn + d4 / 2
        height_calc.append(
            f"距离梁边第4排（最远）：距离梁边第3排中心 + d3/2 + sn + d4/2 = {rc_list[2]:.2f} + {d3}/2 + {sn} + {d4}/2 = {rc_list[3]:.2f}mm")

    # 反转高度列表：匹配原始标注的左远右近顺序（r[0]对应最远，高度最大）
    rc_list_original = rc_list[::-1]
    # 计算面积：按原始标注顺序（左远右近）
    area_list = []
    for i in range(k):
        n, d = r[i]
        area = n * π * (d / 2) ** 2
        area_list.append(round(area, prec_A))
    At = sum([n * π * (d / 2) ** 2 for n, d in r])
    At_fmt = round(At, prec_A)

    # 合力中心计算：按原始标注顺序的面积和对应高度加权平均
    xc = sum(area_list[i] * rc_list_original[i] for i in range(k)) / At
    xc_fmt = round(xc, prec_x)

    # 整理输出用的面积格式（按原始标注顺序）
    A_fmt = {}
    for i in range(k):
        A_fmt[f"A{i + 1}_fmt"] = area_list[i]

    # 返回结果：包含原始标注顺序的高度、面积
    return {
        "r": r,
        "k": k,
        "c": c,
        "dv": dv,
        "sn": sn,
        "rc_list": rc_list_original,  # 原始标注顺序（左远右近）的高度列表
        "At_fmt": At_fmt,
        "xc_fmt": xc_fmt,
        "height_calc": height_calc,
        **A_fmt
    }


# ---------------------- 计算书生成模块（统一无判断） ----------------------
def generate_calc_book(res, r_str):
    """
    独立计算书生成模块（统一按左远右近逻辑输出）
    :param res: calc_core输出的计算结果字典
    :param r_str: 原始平法标注
    :return: 无（直接打印计算书）
    """
    calc_config = " / ".join([f"{n}d{d}" for n, d in res['r']])
    print(f"=== 钢筋保护层与合力中心计算书 ===")
    print(f"原始标注：{r_str}")
    print(f"计算用配置：{calc_config}（左远右近）")
    print(f"计算参数：保护层厚度c={res['c']}mm，箍筋直径dv={res['dv']}mm，排间净距sn={res['sn']}mm，π={π:.4f}")
    print(f"排数：{res['k']}排")
    print(f"计算基准：标注左为距离梁边最远排，右为靠近梁边排，高度从靠近梁边起算")

    print("\n【步骤1：各排中心高度计算】")
    print("高度计算过程（从靠近梁边到最远）：")
    for line in res["height_calc"]:
        print(f"  {line}")
    print("各排中心高度结果（匹配标注左远右近，单位：mm）：")
    for i in range(res["k"]):
        n, d = res['r'][i]
        pos_note = "（最远）" if i == 0 else "（靠近梁边）" if i == res['k'] - 1 else ""
        print(f"  标注第{i + 1}排（{n}d{d}）{pos_note}：{res['rc_list'][i]:.2f}")

    print("\n【步骤2：各排钢筋面积计算（单位：mm²）】")
    for i in range(res["k"]):
        n, d = res['r'][i]
        area_key = f"A{i + 1}_fmt"
        print(f"  标注第{i + 1}排（{n}d{d}）：{res[area_key]}")
    print(f"总面积：{res['At_fmt']}")

    print("\n【步骤3：合力中心计算】")
    if res["k"] >= 2:
        calc_detail = " + ".join([f"{res[f'A{i + 1}_fmt']}×{res['rc_list'][i]:.2f}" for i in range(res["k"])])
        print(f"合力中心计算式：xc=({calc_detail})/{res['At_fmt']}")
    print(f"合力中心位置：距离梁边 {res['xc_fmt']:.2f}mm")
    print("=== 计算结束 ===\n")


# ---------------------- 用户交互模块（主调用入口） ----------------------
def user_interact():
    """用户交互模块（主入口，仅用于判断是否反序）"""
    print("=== 钢筋保护层与合力中心计算程序 ===")
    print("支持平法标注格式：")
    print("1. 斜杠分隔多排：如4d20/4d25、2d18/3d20/2d22/2d25")
    print("2. 排数标注：如9d25 3/3/3、10d25 2/3/5")
    print("3. 单排：如6d22、4d20+2d18")
    print("================================\n")
    r_str = input("请输入平法标注：")
    rebar_pos = input("请输入钢筋位置（top=梁顶，bottom=梁底，默认bottom）：") or "bottom"
    c = int(input("请输入保护层厚度（默认20mm）：") or 20)
    dv = int(input("请输入箍筋直径（默认10mm）：") or 10)
    sn = int(input("请输入排间净距（默认25mm）：") or 25)

    # 解析标注并处理梁顶反序
    r = parse_flat(r_str)
    if rebar_pos == "top":
        r_calc = reverse_top_rebar(r)
    else:
        r_calc = r

    # 计算并生成计算书
    res = calc_core(r_calc, c, dv, sn)
    generate_calc_book(res, r_str)


# ---------------------- 主程序入口 ----------------------
if __name__ == "__main__":
    user_interact()