import plotly.express as px  # 导入plotly的快捷模块（常用别名px）
import plotly.io as pio

# 数据：和之前一致的平方数数据
x_data = [1, 2, 3, 4, 5]
y_data = [1, 4, 9, 16, 25]

# 绘制交互式折线图（原生支持中文，无需额外配置）
fig = px.line(
    x=x_data,
    y=y_data,
    title="平方数折线图",  # 中文标题正常显示
    labels={"x": "数字", "y": "数字的平方"}  # 坐标轴中文标签
)

# 显示图表（会自动在浏览器中打开交互式网页）
fig.show()

# 可选：将图表保存为图片（需要安装kaleido）
# pio.write_image(fig, "square_plot.png")
# 可选：将图表保存为HTML文件
# fig.write_html("square_plot.html")