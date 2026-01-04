# -*- coding: utf-8 -*-
"""
核心功能单元测试
"""
import sys
import os

# 添加项目根目录到sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from concrete.core.beam_rect_fc import beam_rect_fc
from concrete.core.beam_t_fc import beam_t_fc
from concrete.core.rebar import get_params as get_rebar_params
from concrete.core.concrete import get_params as get_concrete_params


def test_concrete_params():
    """测试混凝土参数获取"""
    print("=== 测试混凝土参数获取 ===")
    # 测试规范等级
    c30_params = get_concrete_params(30)
    assert c30_params["fc"] == 14.3
    assert c30_params["ft"] == 1.43
    assert c30_params["Ec"] == 30000
    assert c30_params["α1"] == 1.0
    assert c30_params["β1"] == 0.8
    print("✓ 规范等级C30参数获取成功")
    
    # 测试非标等级
    c37_params = get_concrete_params(37)
    assert c37_params["fc"] > 0
    assert c37_params["ft"] > 0
    assert c37_params["Ec"] > 0
    assert c37_params["α1"] > 0
    assert c37_params["β1"] > 0
    print("✓ 非标等级C37参数获取成功")


def test_rebar_params():
    """测试钢筋参数获取"""
    print("\n=== 测试钢筋参数获取 ===")
    # 测试HRB400钢筋
    hrb400_params = get_rebar_params("HRB400")
    assert hrb400_params["fy"] == 360
    assert hrb400_params["fyc"] == 360
    assert hrb400_params["Es"] == 2.0e5
    assert hrb400_params["ξb"] > 0
    print("✓ HRB400钢筋参数获取成功")
    
    # 测试动态计算ξb
    hrb400_params_c55 = get_rebar_params("HRB400", fcuk=55)
    assert hrb400_params_c55["ξb"] > 0
    print("✓ 动态计算ξb成功")


def test_beam_rect_fc():
    """测试矩形截面梁抗弯承载力计算"""
    print("\n=== 测试矩形截面梁抗弯承载力计算 ===")
    # 测试数据：矩形截面梁
    b = 250  # 腹板宽度(mm)
    h = 500  # 梁总高度(mm)
    fcuk = 30  # 混凝土强度等级C30
    fy_grade = "HRB400"  # 受拉钢筋强度等级
    fyc_grade = "HRB400"  # 受压钢筋强度等级
    Ast = 1520  # 受拉钢筋面积(mm²)（4Φ22）
    ast = 40  # 受拉钢筋合力点至受拉边缘距离(mm)
    Asc = 0  # 受压钢筋面积(mm²)
    asc = 35  # 受压钢筋合力点至受压边缘距离(mm)
    γ0 = 1.0  # 结构重要性系数
    
    result = beam_rect_fc(b, h, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc, γ0)
    x, xb, ξ, ξb, Mu, σs, σsc, check = result
    
    assert x > 0
    assert xb > 0
    assert ξ > 0
    assert ξb > 0
    assert Mu > 0
    assert σs > 0
    assert σsc >= 0
    assert "✓" in check
    print(f"✓ 矩形截面梁计算成功，Mu={Mu} kN·m")


def test_beam_t_fc():
    """测试T形截面梁抗弯承载力计算"""
    print("\n=== 测试T形截面梁抗弯承载力计算 ===")
    # 测试数据：T形截面梁
    b = 250  # 腹板宽度(mm)
    h = 600  # 梁总高度(mm)
    bf = 800  # 翼缘宽度(mm)
    hf = 120  # 翼缘高度(mm)
    fcuk = 30  # 混凝土强度等级C30
    fy_grade = "HRB400"  # 受拉钢筋强度等级
    fyc_grade = "HRB400"  # 受压钢筋强度等级
    Ast = 2011  # 受拉钢筋面积(mm²)（4Φ25）
    ast = 40  # 受拉钢筋合力点至受拉边缘距离(mm)
    Asc = 0  # 受压钢筋面积(mm²)
    asc = 35  # 受压钢筋合力点至受压边缘距离(mm)
    γ0 = 1.0  # 结构重要性系数
    
    result = beam_t_fc(b, h, bf, hf, fcuk, fy_grade, fyc_grade, Ast, ast, Asc, asc, γ0)
    flag, x, xb, ξ, ξb, Mu, σs, σsc, check = result
    
    assert flag in ["第一类T型截面", "第二类T型截面"]
    assert x > 0
    assert xb > 0
    assert ξ > 0
    assert ξb > 0
    assert Mu > 0
    assert σs > 0
    assert σsc >= 0
    assert "✓" in check
    print(f"✓ T形截面梁计算成功，{flag}，Mu={Mu} kN·m")


def main():
    """主测试函数"""
    try:
        test_concrete_params()
        test_rebar_params()
        test_beam_rect_fc()
        test_beam_t_fc()
        print("\n🎉 所有测试通过！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
