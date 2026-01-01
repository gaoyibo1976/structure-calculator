import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties  # 字体管理模块
import warnings

# 关闭警告（可选）
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

# 加载中文字体文件（Windows系统，黑体的ttf文件路径）
# 注意：路径中的斜杠用/或\\，不要用单个\
font = FontProperties(
    fname='C:/Windows/Fonts/simhei.ttf',  # 黑体字体文件的绝对路径
    size=14  # 字体大小
)

# 应用seaborn-v0_8样式
plt.style.use('ggplot')

# 生成数据
x = np.linspace(0, 10, 100)
y = np.sin(x)

# 绘图
plt.figure(figsize=(6, 4))
plt.plot(x, y, label='sin(x)')
# 为中文标题强制指定字体
plt.title('默认样式（美化）', fontproperties=font)
# 如果图例/坐标轴标签有中文，也需要指定：
# plt.xlabel('X轴（数字）', fontproperties=font)
# plt.legend(prop=font)  # 图例的中文需要用prop参数

plt.show()