# rebar.py 钢筋设计指标模块（新增ξb到返回字典）
# 核心：ξb随钢筋参数字典返回，依赖β1（默认0.8，可自定义），对齐concrete.py风格

# -------------------------- 1. 钢筋基础参数（不变） --------------------------
REBAR_PARAMS = {
    "HPB300": {"fy": 270, "fyc": 270, "Es": 2.1e5, "fyk": 300},
    "HRB335": {"fy": 300, "fyc": 300, "Es": 2.0e5, "fyk": 335},
    "HRB400": {"fy": 360, "fyc": 360, "Es": 2.0e5, "fyk": 400},
    "HRB500": {"fy": 435, "fyc": 410, "Es": 2.0e5, "fyk": 500},
    "RRB400": {"fy": 360, "fyc": 360, "Es": 2.0e5, "fyk": 400}
}

# 混凝土极限压应变（规范定值，作为全局常量）
εcu = 0.0033


# -------------------------- 2. 内部辅助：ξb计算（精简） --------------------------
def _calc_xi_b(fy, Es, β1):
    """内部辅助：计算ξb（不对外暴露）"""
    return round(β1 / (1 + fy / (Es * εcu)), 3)


# -------------------------- 3. 核心函数（新增ξb到返回字典） --------------------------
def get_params(grade, β1=0.8):
    """
    获取指定牌号钢筋的完整指标字典（含ξb）
    :param grade: 钢筋牌号（如"HRB400"，兼容小写）
    :param β1: 混凝土等效矩形应力图形系数（默认0.8，C50及以下；C50~C80需传对应值）
    :return: 完整指标字典（fy/fyc/Es/fyk/ξb）
    :raises ValueError: 牌号错误时抛出异常
    """
    # 统一转大写，兼容小写输入
    grade = grade.strip().upper()

    # 校验牌号合法性
    if grade not in REBAR_PARAMS:
        valid_grades = list(REBAR_PARAMS.keys())
        raise ValueError(f"钢筋牌号错误！仅支持：{valid_grades}，输入：{grade}")

    # 获取基础参数 + 计算ξb
    rebar_dict = REBAR_PARAMS[grade].copy()
    rebar_dict["ξb"] = _calc_xi_b(rebar_dict["fy"], rebar_dict["Es"], β1)

    return rebar_dict


# -------------------------- 4. 快捷函数（新增get_rebar_xi_b） --------------------------
def get_fy(grade):
    return get_params(grade)["fy"]


def get_fyc(grade):
    return get_params(grade)["fyc"]


def get_Es(grade):
    return get_params(grade)["Es"]


def get_fyk(grade):
    return get_params(grade)["fyk"]


def get_xi_b(grade, β1=0.8):
    """快捷获取ξb（支持自定义β1）"""
    return get_params(grade, β1)["ξb"]


# -------------------------- 5. 示例调用（展示ξb获取） --------------------------
if __name__ == "__main__":
    # 示例1：默认β1=0.8（C50及以下），获取含ξb的完整字典
    hrb400_params = get_params("HRB400")
    print("HRB400完整指标（含ξb）：", hrb400_params)
    # 输出：{'fy': 360, 'fyc': 360, 'Es': 200000.0, 'fyk': 400, 'ξb': 0.518}

    # 示例2：自定义β1=0.79（C55混凝土），获取ξb
    hrb400_params_c55 = get_params("HRB400", β1=0.79)
    print("HRB400（C55，β1=0.79）的ξb：", hrb400_params_c55["ξb"])
    # 输出：0.512

    # 示例3：快捷函数获取ξb
    xi_b_hrb500 = get_xi_b("HRB500")
    print("HRB500的ξb：", xi_b_hrb500)
    # 输出：0.482

    # 示例4：一次性解包多个指标（含ξb），对齐concrete.py调用风格
    hrb400 = get_params("HRB400")
    fy, Es, ξb = hrb400["fy"], hrb400["Es"], hrb400["ξb"]
    print(f"HRB400: fy={fy}, Es={Es}, ξb={ξb}")