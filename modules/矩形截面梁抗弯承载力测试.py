from beam_rect_fc import beam_rect_fc
from report_beam_rect import report_beam_rect_fc

# 矩形截面梁测试数据
param = [
    {
        "sec_id": " ",
        "calc_params": [250,500,30,"HRB400","HRB400",1500,42.5,0,42.5]
    },
    {
        "sec_id": " ",
        "calc_params": [250,500,30,"HRB400","HRB400",1500,42.5,1000,42.5]
    },
    {
        "sec_id": " ",
        "calc_params": [250,500,30,"HRB400","HRB400",2500,42.5,1000,42.5]
    },
    {
        "sec_id": " ",
        "calc_params": [250,500,30,"HRB400","HRB400",7000,42.5,500,42.5]
    },
    {
        "sec_id": " ",
        "calc_params": [250,500,30,"HRB400","HRB400",8000,42.5,500,42.5]
    }
]
count_rect = len(param)
# 循环：提取编号和计算参数
num = 1  # num = 计算顺序（第几个截面）
for item in param:
    # 核心修改：拼接成「计算顺序-截面自身编号」，清晰区分（如 "1-1"、"2-2"）
    sec_id = f"序号{count_rect}.{num}      编号：{item['sec_id']}"  # 格式：计算顺序-截面编号
    calc_p = item["calc_params"]
    result = beam_rect_fc(*calc_p)  # 仅传计算参数，数量匹配
    report = report_beam_rect_fc(sec_id, calc_p, result)
    print(report)
    num += 1
print(f"{"=" * 30}\n【END】" )