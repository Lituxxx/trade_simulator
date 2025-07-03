import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os
import random


# 设置页面配置
st.set_page_config(
    page_title="A股炒股模拟器",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 隐藏Streamlit默认的汉堡菜单和页脚
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 数据目录 - 固定为本地stockdata文件夹
data_dir = "stockdata"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
    st.info(f"已创建{data_dir}文件夹用于存储股票数据")

# 数据加载函数
@st.cache_data
def load_stock_data(file_path):
    try:
        df = pd.read_csv(file_path)
        # 确保日期列存在且格式正确
        if 'trade_date' in df.columns:
            df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
            df = df.sort_values('trade_date')
            return df
        else:
            st.error("'trade_date' not found")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

@st.cache_data
def get_available_stocks(data_dir):
    if not os.path.exists(data_dir):
        return []
    
    stock_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    return stock_files

# 交易模拟器类
class StockTrader:
    def __init__(self, initial_capital=100000, commission_rate=0.0003):
        """初始化交易模拟器"""
        self.initial_capital = initial_capital  # 初始资金
        self.capital = initial_capital          # 当前资金
        self.shares = 0                         # 持有的股票数量
        self.commission_rate = commission_rate  # 交易费率
        self.trade_history = []                 # 交易历史
        self.daily_state = []                   # 每日状态记录
        
    def buy(self, date, price, amount, stock_code):
        """买入股票"""
        total_cost = price * amount * (1 + self.commission_rate)
        
        if total_cost > self.capital:
            return False, "insufficient fund"
        
        self.capital -= total_cost
        self.shares += amount
        
        self.trade_history.append({
            'date': date,
            'type': '买入',
            'stock_code': stock_code,
            'price': price,
            'amount': amount,
            'total_cost': total_cost
        })
        
        return True, f"买入成功: {amount}股，价格: {price}元，总成本: {total_cost:.2f}元"
    
    def sell(self, date, price, amount, stock_code):
        """卖出股票"""
        if amount > self.shares:
            return False, "股票数量不足，卖出失败"
        
        total_income = price * amount * (1 - self.commission_rate)
        
        self.capital += total_income
        self.shares -= amount
        
        self.trade_history.append({
            'date': date,
            'type': '卖出',
            'stock_code': stock_code,
            'price': price,
            'amount': amount,
            'total_income': total_income
        })
        
        return True, f"卖出成功: {amount}股，价格: {price}元，总收入: {total_income:.2f}元"
    
    def record_daily_state(self, date, price):
        """记录每日状态"""
        portfolio_value = self.capital + self.shares * price
        daily_return = 0 if not self.daily_state else (price / self.daily_state[-1]['price'] - 1) * 100
        cumulative_return = (portfolio_value / self.initial_capital - 1) * 100
        
        self.daily_state.append({
            'date': date,
            'price': price,
            'capital': self.capital,
            'shares': self.shares,
            'portfolio_value': portfolio_value,
            'daily_return': daily_return,
            'cumulative_return': cumulative_return
        })
        
        return daily_return, cumulative_return
    
    def get_current_portfolio_value(self, current_price):
        """获取当前投资组合价值"""
        return self.capital + self.shares * current_price
    
    def get_trade_history_df(self):
        """获取交易历史DataFrame"""
        return pd.DataFrame(self.trade_history)
    
    def get_daily_state_df(self):
        """获取每日状态DataFrame"""
        return pd.DataFrame(self.daily_state)
    
    def has_buy_transaction(self):
        """检查是否有买入交易"""
        for trade in self.trade_history:
            if trade['type'] == '买入':
                return True
        return False

# 绘制K线图
def plot_candlestick(df, start_idx, end_idx, highlight_idx=None):
    """绘制K线图"""
    fig, ax = plt.subplots(figsize=(14, 7))  # 增大图表尺寸以便查看更多数据
    
    # 切片数据
    plot_data = df.iloc[start_idx:end_idx]
    
    # 绘制K线
    for i, row in plot_data.iterrows():
        date = mdates.date2num(row['trade_date'])
        open_price = row['open']
        close_price = row['close']
        high_price = row['high']
        low_price = row['low']
        
        # 上涨为绿色，下跌为红色
        color = 'g' if close_price >= open_price else 'r'
        
        # 绘制实体
        ax.bar(date, close_price - open_price, width=0.6, bottom=open_price, color=color)
        
        # 绘制上下影线
        ax.vlines(date, low_price, high_price, color=color)
        
        # 高亮当前日期
        if i == highlight_idx:
            ax.bar(date, close_price - open_price, width=0.8, bottom=open_price, color='yellow', alpha=0.5)
            ax.vlines(date, low_price, high_price, color='yellow', linewidth=2)
    
    # 设置X轴为日期格式
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    
    # 设置标题和标签
    plt.title(f"股票K线图 ({plot_data['trade_date'].min().strftime('%Y-%m-%d')} 至 {plot_data['trade_date'].max().strftime('%Y-%m-%d')})")
    plt.xlabel('日期')
    plt.ylabel('价格 (元)')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    return fig

# 主函数
def main():
    st.title("A股炒股模拟器")
    
    # 初始化会话状态
    if 'mode_selected' not in st.session_state:
        st.session_state.mode_selected = "manual"  # 默认手动模式
    if 'stock_data_loaded' not in st.session_state:
        st.session_state.stock_data_loaded = False
    if 'selected_stock_loaded' not in st.session_state:
        st.session_state.selected_stock_loaded = None
    if 'auto_loaded' not in st.session_state:
        st.session_state.auto_loaded = False
    if 'trading_days' not in st.session_state:
        st.session_state.trading_days = 500  # 设置默认显示500个交易日
    if 'buy_executed' not in st.session_state:
        st.session_state.buy_executed = False  # 标记是否执行了买入操作
    
    # 侧边栏 - 模式选择和数据导入
    with st.sidebar:
        st.header("模式选择")
        # 模式选择
        mode = st.radio("选择操作模式", ["手动选择", "随机抽取"], 
                       key="mode_radio", 
                       help="手动选择: 从本地stockdata文件夹中选择单个股票文件\n随机抽取: 从stockdata文件夹中随机选择股票")
        
        # 更新会话状态中的模式
        if mode != st.session_state.mode_selected:
            st.session_state.mode_selected = mode
            # 重置相关状态
            st.session_state.stock_data_loaded = False
            st.session_state.selected_stock_loaded = None
            st.session_state.auto_loaded = False
        
        # 根据模式显示不同的导入界面
        if mode == "手动选择":
            st.subheader("从本地选择股票数据")
            # 获取可用的股票数据
            available_stocks = get_available_stocks(data_dir)
            
            if not available_stocks:
                st.warning(f"在{data_dir}文件夹中未找到CSV文件，请先手动导入股票数据或上传文件")
                # 提供文件上传功能
                uploaded_file = st.file_uploader("请上传一个CSV文件", type=["csv"])
                
                if uploaded_file is not None:
                    # 直接加载上传的文件，不保存到磁盘
                    try:
                        df = pd.read_csv(uploaded_file)
                        if 'trade_date' in df.columns:
                            df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
                            df = df.sort_values('trade_date')
                            st.session_state.stock_data = df
                            st.session_state.stock_data_loaded = True
                            file_name = uploaded_file.name
                            st.session_state.selected_file = file_name
                            st.session_state.selected_stock_loaded = os.path.splitext(file_name)[0]
                            st.success("数据加载成功！")
                        else:
                            st.error("数据文件中未找到'trade_date'列")
                    except Exception as e:
                        st.error(f"文件加载失败: {e}")
            else:
                # 显示文件选择下拉框
                selected_file = st.selectbox("选择股票数据文件", available_stocks)
                
                if st.button("加载选中的股票"):
                    file_path = os.path.join(data_dir, selected_file)
                    stock_data = load_stock_data(file_path)
                    if not stock_data.empty:
                        st.session_state.stock_data = stock_data
                        st.session_state.stock_data_loaded = True
                        st.session_state.selected_file = selected_file
                        st.session_state.selected_stock_loaded = os.path.splitext(selected_file)[0]
                        st.success(f"已加载股票: {os.path.splitext(selected_file)[0]}")
                    else:
                        st.error("数据加载失败，请检查文件格式")
        else:  # 随机抽取模式
            st.subheader("从stockdata文件夹中随机抽取股票")
            # 获取可用的股票数据
            available_stocks = get_available_stocks(data_dir)
            
            if not available_stocks:
                st.error(f"在{data_dir}文件夹中未找到CSV文件，请先手动导入股票数据")
            else:
                if st.button("随机选择股票"):
                    # 随机抽取一个文件
                    selected_file = random.choice(available_stocks)
                    selected_stock = os.path.splitext(selected_file)[0]
                    st.info(f"已随机选择: {selected_stock}")
                    
                    # 自动加载随机选择的文件
                    file_path = os.path.join(data_dir, selected_file)
                    stock_data = load_stock_data(file_path)
                    if not stock_data.empty:
                        st.session_state.stock_data = stock_data
                        st.session_state.selected_file = selected_file
                        st.session_state.selected_stock_loaded = selected_stock
                        st.session_state.auto_loaded = True
                        st.session_state.stock_data_loaded = True
                        st.success("已自动加载随机选择的股票数据")
                    else:
                        st.error("数据加载失败，请检查文件")
        
        # 仅在数据已加载时显示参数设置
        if st.session_state.stock_data_loaded:
            st.header("交易参数设置")
            
            # 检查是否已执行买入操作
            if 'trader' in st.session_state:
                st.session_state.buy_executed = st.session_state.trader.has_buy_transaction()
            
            # 初始资金 - 根据是否执行买入操作决定是否禁用
            if st.session_state.buy_executed:
                initial_capital = st.number_input(
                    "初始资金(元)", 
                    min_value=1000, 
                    value=st.session_state.trader.initial_capital, 
                    step=1000,
                    disabled=True
                )
                st.info("已执行买入操作，初始资金不可调整。如需重新设置，请点击下方的'重置模拟器'按钮。")
            else:
                initial_capital = st.number_input(
                    "初始资金(元)", 
                    min_value=1000, 
                    value=100000, 
                    step=1000
                )
            
            # 交易费率
            commission_rate = st.slider("交易费率(%)", min_value=0.01, max_value=0.3, value=0.03, step=0.01) / 100
            
            # 初始化交易模拟器
            if 'trader' not in st.session_state:
                st.session_state.trader = StockTrader(initial_capital, commission_rate)
            
            # 重置按钮
            if st.button("重置模拟器"):
                st.session_state.trader = StockTrader(initial_capital, commission_rate)
                st.session_state.current_day = 499  # 初始显示第1-500条数据
                st.session_state.buy_executed = False  # 重置买入标记
                st.success("模拟器已重置")
    
    # 主界面逻辑 (仅在数据加载后显示)
    if hasattr(st.session_state, 'stock_data') and not st.session_state.stock_data.empty and st.session_state.stock_data_loaded:
        stock_data = st.session_state.stock_data
        selected_stock = st.session_state.selected_stock_loaded
        total_days = len(stock_data)
        
        # 初始化当前日期索引（调整为从第500条数据开始）
        if 'current_day' not in st.session_state:
            st.session_state.current_day = min(499, total_days - 1)  # 初始显示第1-500条，或全部数据
        
        # 获取当前日期索引并确保不超出范围
        current_day = st.session_state.current_day
        current_day = min(current_day, total_days - 1)
        current_day = max(current_day, 499)  # 确保至少显示500条数据
        
        # 计算显示范围（固定显示500条数据，随时间推移滑动窗口）
        start_idx = current_day - 499
        end_idx = current_day + 1
        
        # 确保start_idx不小于0
        start_idx = max(0, start_idx)
        end_idx = min(end_idx, total_days)
        
        # 当数据不足500条时，显示全部数据
        if total_days < 500:
            start_idx = 0
            end_idx = total_days
            current_day = total_days - 1
        
        # 获取当前日期数据
        if current_day < total_days:
            current_data = stock_data.iloc[current_day]
            current_date = current_data['trade_date'].strftime('%Y-%m-%d')
            current_price = current_data['close']
        else:
            current_date = "数据已结束"
            current_price = 0
        
        # 显示当前状态
        col1, col2, col3 = st.columns(3)
        col1.metric("当前日期", current_date)
        col1.metric("当前价格", f"{current_price:.2f}元")
        
        # 记录每日状态
        if current_day < total_days:
            daily_return, cumulative_return = st.session_state.trader.record_daily_state(
                current_date, current_price
            )
            col2.metric("当日收益率", f"{daily_return:.2f}%")
            col2.metric("累积收益率", f"{cumulative_return:.2f}%")
            
            current_value = st.session_state.trader.get_current_portfolio_value(current_price)
            col3.metric("当前总资产", f"{current_value:.2f}元")
            col3.metric("持仓数量", f"{st.session_state.trader.shares}股")
        else:
            col2.metric("当日收益率", "数据已结束")
            col2.metric("累积收益率", "数据已结束")
            col3.metric("当前总资产", "数据已结束")
            col3.metric("持仓数量", f"{st.session_state.trader.shares}股")
        
        # 绘制K线图
        st.subheader(f"股票K线图 (第{start_idx+1}至第{end_idx}个交易日)")
        if end_idx > start_idx:
            fig = plot_candlestick(stock_data, start_idx, end_idx, current_day - start_idx)
            st.pyplot(fig)
        else:
            st.info("数据不足，无法绘制K线图")
        
        # 交易控制
        st.subheader("交易操作")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("前进一天") and current_day < total_days - 1:
                st.session_state.current_day += 1
                st.rerun()
            elif current_day >= total_days - 1:
                st.info("已到达数据末尾")
        
        with col2:
            if st.button("前进一周"):
                new_day = current_day + 7
                if new_day < total_days:
                    st.session_state.current_day = new_day
                else:
                    st.session_state.current_day = total_days - 1
                st.rerun()
        
        with col3:
            if st.button("前进一月"):
                new_day = current_day + 30
                if new_day < total_days:
                    st.session_state.current_day = new_day
                else:
                    st.session_state.current_day = total_days - 1
                st.rerun()
        
        # 交易表单
        st.subheader("交易决策")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if current_day < total_days:
                action = st.radio("交易动作", ["买入", "卖出", "持有"])
            else:
                action = "持有"
                st.info("已到达数据末尾，无法进行交易")
        
        with col2:
            if current_day < total_days and action in ["买入", "卖出"]:
                if action == "买入":
                    max_buyable = int(st.session_state.trader.capital / (current_price * (1 + commission_rate)))
                    amount = st.number_input(f"买入数量 (最大: {max_buyable})", 
                                            min_value=1, 
                                            value=max(1, max_buyable // 2), 
                                            step=1)
                else:  # 卖出
                    amount = st.number_input(f"卖出数量 (最大: {st.session_state.trader.shares})", 
                                            min_value=1, 
                                            value=st.session_state.trader.shares // 2, 
                                            step=1)
            else:
                amount = 0
        
        with col3:
            if current_day < total_days and st.button("执行交易") and action != "持有":
                if action == "买入":
                    success, message = st.session_state.trader.buy(
                        current_date, current_price, amount, selected_stock
                    )
                    if success:
                        st.session_state.buy_executed = True  # 标记已执行买入操作
                else:  # 卖出
                    success, message = st.session_state.trader.sell(
                        current_date, current_price, amount, selected_stock
                    )
                
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        # 显示交易历史
        st.subheader("交易历史")
        trade_history_df = st.session_state.trader.get_trade_history_df()
        if not trade_history_df.empty:
            st.dataframe(trade_history_df)
        
        # 显示每日状态
        st.subheader("每日收益曲线")
        daily_state_df = st.session_state.trader.get_daily_state_df()
        if not daily_state_df.empty:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(daily_state_df['date'], daily_state_df['cumulative_return'], 'b-', label='累积收益率')
            ax.set_xlabel('日期')
            ax.set_ylabel('收益率 (%)')
            ax.set_title('累积收益率曲线')
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.legend()
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.info("暂无收益数据")
    else:
        if st.session_state.mode_selected == "manual" and not st.session_state.stock_data_loaded:
            st.info("请选择'手动选择'模式并从stockdata文件夹中选择股票数据文件，或上传新的股票数据文件")
        elif st.session_state.mode_selected == "random" and not st.session_state.stock_data_loaded:
            st.info("请选择'随机抽取'模式并点击'随机选择股票'按钮")

if __name__ == "__main__":
    main()