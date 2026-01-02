
def get_rebar(grade):
    """获取钢筋材料参数（fy、ξb、Es）"""
    rebar_params = {
        "HRB400": (360, 0.550, 2e5),
        "HRB500": (435, 0.482, 2e5)
    }
    return rebar_params.get(grade, rebar_params["HRB400"])
