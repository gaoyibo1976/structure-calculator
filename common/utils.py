import re

# =========== 线性内插函数 ============
def linear_interp(x, x1, x2, y1, y2):
    """
    通用线性插值函数（抽离到工具模块，所有场景复用）
    :param x: 当前待插值的值（如37）
    :param x1: 左参考点数值（如35）
    :param x2: 右参考点数值（如40）
    :param y1: 左参考点对应结果（如0.13）
    :param y2: 右参考点对应结果（如0.12）
    :return: 线性插值结果
    """
    return y1 + (y2 - y1) * (x - x1) / (x2 - x1)

# ========== 通用公式计算函数（支持自定义小数位数+乘号防混淆） ==========
def calc_formula(f, p, prec=None):
    """
    通用公式计算：
    :param f: 公式模板
    :param p: 参数字典
    :param prec: 小数位字典（如{"fy":1, "As":2}），默认None则按工程规范处理
    :return: res(结果), fp(美化公式), fe(美化代入式)
    """
    default_prec = {
        "b":0, "h":0, "d":0, "n":0,  # 几何尺寸：整数
        "fc":1, "fy":1, "ft":1,      # 材料强度：1位小数
        "As":2, "ρmin":4, "ρ":4,     # 钢筋面积：2位；配筋率：4位
        "α1":1, "ξb":3, "εcu":4,     # 系数：1-4位
        "x":2, "h0":2, "ξ":4,        # 几何参数：2-4位
        "Mu":2, "σs":2               # 承载力/应力：2位
    }
    if prec is None:
        prec = default_prec
    # 美化公式原型
    fp = f.replace("*", "·").replace("/", "÷").replace("(", "（").replace(")", "）")
    if "/" in f and "(" in f and f.count("(")>=2 and f.count(")")>=2:
        num, den = re.split(r"/(?=\()", f, 1)
        fp = f"{num.strip('()').replace('*','·')}\n————\n{den.strip('()').replace('*','·')}"
    # 生成数值代入式
    fe = f
    for k, v in p.items():
        n = prec.get(k, 2)
        if isinstance(v, int) or v.is_integer():
            val_str = f"{int(v)}"
        else:
            val_str = f"{v:.{n}f}"
        fe = re.sub(rf"\b{k}\b", val_str, fe)
    fe = fe.replace("*", "×").replace("/", "÷").replace("(", "（").replace(")", "）")
    if "/" in f and "(" in f and fe.count("(")>=2 and fe.count(")")>=2:
        num, den = re.split(r"/(?=\()", fe, 1)
        fe = f"{num.strip('()').replace('*','×')}\n————\n{den.strip('()').replace('*','×')}"
    # 计算结果
    exec_f = f
    for k, v in p.items():
        exec_f = re.sub(rf"\b{k}\b", str(v), exec_f)
    res = eval(exec_f)
    return res, fp, fe