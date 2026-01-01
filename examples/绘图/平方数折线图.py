import matplotlib.pyplot as plt
import matplotlib  # 新增：导入matplotlib主模块

# 核心配置：解决中文显示问题
# 1. 指定默认字体：选择支持中文的字体（Windows用SimHei，Mac用PingFang SC）
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # Windows
# matplotlib.rcParams['font.sans-serif'] = ['PingFang SC']  # Mac/Linux（根据系统调整）
# 2. 解决负号显示为方块的问题（可选，比如绘图中有负数时需要）
matplotlib.rcParams['axes.unicode_minus'] = False
# 3. 关闭字体缺失的警告（可选，让控制台更干净）
matplotlib.rcParams['font.family'] = 'sans-serif'

# 原有代码
squares = [1,4,9,16,25]
fig, ax = plt.subplots()
ax.plot(range(-4,1), squares,linewidth=3)
# 中文标题和标签
ax.set_title("平方数折线图", fontsize=16)
ax.set_xlabel("数字", fontsize=12)
ax.set_ylabel("数字的平方", fontsize=12)
# 设置刻度和刻度文字大小
ax.tick_params(axis='both', labelsize=10)
plt.show()