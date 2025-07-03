import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 设置页面配置
st.set_page_config(
    page_title="Streamlit测试应用",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 页面标题
st.title("Streamlit功能测试")
st.write("这个应用展示了Streamlit的基本功能和组件。")

# 侧边栏
with st.sidebar:
    st.header("配置选项")
    
    # 选择框
    chart_type = st.selectbox(
        "选择图表类型",
        ["折线图", "柱状图", "散点图"]
    )
    
    # 滑块
    num_points = st.slider(
        "数据点数量",
        min_value=10,
        max_value=100,
        value=50,
        step=5
    )
    
    # 复选框
    show_table = st.checkbox("显示数据表格", value=True)
    
    # 颜色选择器
    color = st.color_picker("选择图表颜色", "#1f77b4")
    
    # 按钮
    if st.button("重置配置"):
        st.session_state.clear()
        st.experimental_rerun()

# 主内容区
st.header("数据可视化")

# 生成随机数据
np.random.seed(42)
x = np.linspace(0, 10, num_points)
y = np.sin(x) + np.random.normal(0, 0.3, num_points)

# 创建数据框
data = pd.DataFrame({
    'x轴': x,
    'y轴': y
})

# 显示数据表格
if show_table:
    st.subheader("数据表格")
    st.dataframe(data)

# 绘制图表
st.subheader(f"{chart_type}展示")

if chart_type == "折线图":
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, y, color=color, linewidth=2)
    ax.set_title("随机生成的折线图")
    ax.set_xlabel("X轴")
    ax.set_ylabel("Y轴")
    ax.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(fig)

elif chart_type == "柱状图":
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x, y, color=color, width=0.15)
    ax.set_title("随机生成的柱状图")
    ax.set_xlabel("X轴")
    ax.set_ylabel("Y轴")
    ax.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(fig)

else:  # 散点图
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(x, y, color=color, s=50, alpha=0.7)
    ax.set_title("随机生成的散点图")
    ax.set_xlabel("X轴")
    ax.set_ylabel("Y轴")
    ax.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(fig)

# 交互组件示例
st.header("交互组件演示")

# 按钮示例
if st.button("点击我"):
    st.success("按钮点击成功！")

# 文本输入
name = st.text_input("输入你的名字", "")
if name:
    st.write(f"你好，{name}！")

# 数字输入
age = st.number_input("输入你的年龄", min_value=0, max_value=120, value=30)
st.write(f"你的年龄是：{age}岁")

# 单选按钮
gender = st.radio("选择你的性别", ["男", "女", "其他"])
st.write(f"你的性别是：{gender}")

# 文件上传
uploaded_file = st.file_uploader("上传文件", type=["txt", "csv", "pdf"])
if uploaded_file is not None:
    st.write(f"已上传文件：{uploaded_file.name}")

# 进度条
progress_bar = st.progress(0)
status_text = st.empty()

for i in range(101):
    progress_bar.progress(i)
    status_text.text(f"进度：{i}%")
    if i == 100:
        status_text.text("完成！")

# 警告消息
st.warning("这是一个警告消息示例")

# 错误消息
st.error("这是一个错误消息示例")

# 信息消息
st.info("这是一个信息消息示例")

# 成功消息
st.success("这是一个成功消息示例")

# 页面底部
st.write("---")
st.write("感谢测试Streamlit！")