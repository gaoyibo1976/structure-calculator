from beam_rect_fc import beam_rect_fc
from report_beam_rect import report_beam_rect_fc

# 矩形截面梁测试数据
param = [
    {
        "sec_id": " ",
        "calc_params": [250, 500, 30, "HRB400", "HRB400", 1500, 42.5, 0, 42.5]
    },
    {
        "sec_id": " ",
        "calc_params": [250, 500, 30, "HRB400", "HRB400", 1500, 42.5, 1000, 42.5]
    },
    {
        "sec_id": " ",
        "calc_params": [250, 500, 30, "HRB400", "HRB400", 2500, 42.5, 1000, 42.5]
    },
    {
        "sec_id": " ",
        "calc_params": [250, 500, 30, "HRB400", "HRB400", 7000, 42.5, 500, 42.5]
    },
    {
        "sec_id": " ",
        "calc_params": [250, 500, 30, "HRB400", "HRB400", 8000, 42.5, 500, 42.5]
    }
]
count_rect = len(param)

# 核心新增：定义文件路径（当前目录）
file_path = "矩形截面抗弯承载力计算结果.out"

# 打开文件（w模式清空重写，a模式追加；utf-8编码防中文乱码）
with open(file_path, "w", encoding="utf-8") as f:
    # 循环：提取编号和计算参数（保留你原有逻辑）
    num = 1  # num = 计算顺序（第几个截面）
    for item in param:
        # 保留你原有sec_id拼接格式
        sec_id = f"序号{count_rect}.{num}      编号：{item['sec_id']}"
        calc_p = item["calc_params"]
        result = beam_rect_fc(*calc_p)  # 仅传计算参数，数量匹配
        report = report_beam_rect_fc(sec_id, calc_p, result)

        # 1. 控制台打印（保留原有）
        print(report)
        # 2. 写入文件（和控制台输出一致，加换行保证格式）
        f.write(report + "\n")

        num += 1

    # 保留你原有结束标识
    end_str = f"{'=' * 30}\n【END】"
    print(end_str)
    # 结束标识也写入文件
    f.write(end_str)

# 控制台提示文件写入完成
print(f"\n✅ 计算结果已写入文件：{file_path}（当前目录）")