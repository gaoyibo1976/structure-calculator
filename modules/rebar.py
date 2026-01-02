# rebar.py 钢筋设计指标模块（GB 50010-2010/2015版）
# 核心：嵌套字典存储+灵活获取函数，易维护、易调用

# -------------------------- 1. 钢筋设计指标基础数据（嵌套字典，已删除ξb） --------------------------
# 外层key：钢筋牌号 | 内层key：设计指标（规范统一命名）
# 指标说明：
# fy: 抗拉强度设计值 (N/mm²)
# fyc: 抗压强度设计值 (N/mm²)
# Es: 弹性模量 (N/mm²，×10^5)
# fyk: 屈服强度标准值 (N/mm²)
REBAR_PARAMS = {
    "HPB300": {
        "fy": 270,
        "fyc": 270,
        "Es": 2.1e5,
        "fyk": 300
    },
    "HRB335": {
        "fy": 300,
        "fyc": 300,
        "Es": 2.0e5,
        "fyk": 335
    },
    "HRB400": {
        "fy": 360,
        "fyc": 360,
        "Es": 2.0e5,
        "fyk": 400
    },
    "HRB500": {
        "fy": 435,
        "fyc": 410,  # 抗压强度设计值≠抗拉（规范特殊规定）
        "Es": 2.0e5,
        "fyk": 500
    },
    "RRB400": {
        "fy": 360,
        "fyc": 360,
        "Es": 2.0e5,
        "fyk": 400
    }
}


# -------------------------- 2. 核心调用函数 --------------------------
def get_rebar_params(grade, keys=None):
    """
    获取指定牌号钢筋的设计指标
    :param grade: 钢筋牌号（如"HRB400"）
    :param keys: 要获取的指标key，可选：
                 - None → 返回该牌号全部指标字典
                 - 单个字符串（如"fy"）→ 返回单个值
                 - 列表（如["fy", "fyc"]）→ 返回元组
    :return: 字典/单个值/元组（匹配keys格式）
    :raises ValueError: 牌号不存在或指标key错误时抛出异常
    """
    # 第一步：校验钢筋牌号是否合法
    grade = grade.strip().upper()  # 统一转大写，兼容小写输入（如"hrb400"）
    if grade not in REBAR_PARAMS:
        valid_grades = list(REBAR_PARAMS.keys())
        raise ValueError(f"钢筋牌号错误！仅支持：{valid_grades}，输入为：{grade}")

    # 第二步：获取该牌号的全部指标
    rebar_dict = REBAR_PARAMS[grade]

    # 第三步：根据keys返回对应结果
    if keys is None:
        # 返回全部指标字典
        return rebar_dict.copy()  # 返回副本，避免修改原字典
    elif isinstance(keys, str):
        # 返回单个指标值
        if keys not in rebar_dict:
            valid_keys = list(rebar_dict.keys())
            raise ValueError(f"指标key错误！{grade}仅支持：{valid_keys}，输入为：{keys}")
        return rebar_dict[keys]
    elif isinstance(keys, (list, tuple)):
        # 返回多个指标的元组
        result = []
        for k in keys:
            if k not in rebar_dict:
                valid_keys = list(rebar_dict.keys())
                raise ValueError(f"指标key错误！{grade}仅支持：{valid_keys}，输入为：{k}")
            result.append(rebar_dict[k])
        return tuple(result)
    else:
        raise TypeError("keys仅支持：None/字符串/列表/元组")


# -------------------------- 3. 辅助函数（可选，简化常用调用） --------------------------
def get_rebar_fy(grade):
    """快捷获取抗拉强度设计值"""
    return get_rebar_params(grade, "fy")


def get_rebar_fyc(grade):
    """快捷获取抗压强度设计值"""
    return get_rebar_params(grade, "fyc")


def get_rebar_Es(grade):
    """快捷获取弹性模量"""
    return get_rebar_params(grade, "Es")

# 新增ξb计算函数（可放在rebar.py或梁计算模块中）
def calc_xi_b(fy, Es, β1=0.8, εcu=0.0033):
    """
    计算相对界限受压区高度ξb
    :param fy: 钢筋抗拉强度设计值 (N/mm²)
    :param Es: 钢筋弹性模量 (N/mm²)
    :param β1: 等效矩形应力图形系数（C50及以下取0.8，C50~C80线性递减）
    :param εcu: 混凝土极限压应变（规范取0.0033）
    :return: ξb（相对界限受压区高度）
    """
    # 规范公式：ξb = β1 / [1 + fy/(Es×ecu)]
    ξb = β1 / (1 + fy / (Es * εcu))
    return round(ξb, 3)  # 保留3位小数，符合工程精度

# 调用示例（结合rebar模块）
if __name__ == "__main__":
    # 先获取钢筋的fy、Es，再计算ξb
    fy = get_rebar_fy("HRB400")
    Es = get_rebar_Es("HRB400")
    xi_b = calc_xi_b(fy, Es)
    print(f"HRB400的ξb（计算值）：{xi_b}")  # 输出：0.518（和规范值一致）

# -------------------------- 4. 示例调用（测试用，已删除ξb相关） --------------------------
if __name__ == "__main__":
    # 示例1：获取HRB400的全部指标
    hrb400_all = get_rebar_params("HRB400")
    print("HRB400全部指标：", hrb400_all)

    # 示例2：仅获取HRB400的fy（抗拉）
    hrb400_fy = get_rebar_params("HRB400", "fy")
    print("HRB400抗拉强度设计值fy：", hrb400_fy)

    # 示例3：同时获取fy、fyc、Es（常用组合）
    hrb400_core = get_rebar_params("HRB400", ["fy", "fyc", "Es"])
    print("HRB400核心指标(fy, fyc, Es)：", hrb400_core)

    # 示例4：快捷函数调用（更简洁）
    hrb500_fyc = get_rebar_fyc("HRB500")
    print("HRB500抗压强度设计值fyc：", hrb500_fyc)