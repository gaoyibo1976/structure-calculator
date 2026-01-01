# 结构计算.py
# 导入混凝土设计指标模块（注意两个文件要放在同一目录下）
import concrete_core_indices as concrete

# 示例1：调用C30的核心指标（f_cuk=30）
f_cuk = float(input("请输入混凝土强度等级："))
f_tk, f_t, f_ck, f_c, E_c = concrete.get_concrete_core_indices(f_cuk)
f_c1 = concrete.get_concrete_core_indices(f_cuk)[3]
# 输出指标，用于后续结构计算
print(f"=== C{int(f_cuk)}混凝土核心设计指标 ===")
print(f"轴心抗拉强度标准值f_tk：{f_tk} N/mm²")
print(f"轴心抗拉强度设计值f_t：{f_t} N/mm²")
print(f"轴心抗压强度标准值f_ck：{f_ck} N/mm²")
print(f"轴心抗压强度设计值f_c：{f_c} N/mm²")
print(f"弹性模量E_c：{E_c} N/mm²")
print(f"轴心抗压强度设计值f_c1：{f_c1} N/mm²")
# 示例2：调用非规范值（f_cuk=35.5）的指标，用于结构计算
f_cuk2 = 35.5
indices = concrete.get_concrete_core_indices(f_cuk2)
# 用指标进行结构计算（示例：计算抗压承载力）
bearing_capacity = f_c * 1000  # 假设截面面积为1000 mm²
print(f"\n=== f_cuk=35.5的混凝土抗压承载力 ===")
print(f"抗压承载力：{bearing_capacity} N")