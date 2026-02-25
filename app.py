import streamlit as st
import pandas as pd
import plotly.express as px

# === 网页全局设置 ===
st.set_page_config(page_title="超话排名实时监控", page_icon="📈", layout="wide")
st.title("📈 游戏角色超话前7名 24h 激战看板")

@st.cache_data(ttl=600)
def load_data():
    try:
        df = pd.read_csv("game_character_top7.csv")
        df['时间'] = pd.to_datetime(df['时间'])
        return df
    except Exception as e:
        return None

df = load_data()

if df is not None and not df.empty:
    # 1. 映射你指定的“代号”
    name_mapping = {
        '秦彻': '厕',
        '恋与深空黎深': '黎神',
        '祁煜': '穆棱',
        '沈星回': '猪',
        '齐司礼': '齐司礼',
        '夏以昼': '骨灰', 
        '光与夜之恋陆沉': '光与夜之恋陆沉'
    }
    
    # 将 CSV 里的“角色名”替换为你的“代号”
    df['显示名称'] = df['角色名'].map(name_mapping).fillna(df['角色名'])

    # 2. 映射你指定的“专属颜色” (使用十六进制颜色码)
    color_mapping = {
        '厕': '#FF0000',          # 红色
        '黎神': '#0000FF',        # 蓝色
        '穆棱': '#FF69B4',        # 粉色
        '猪': '#800080',          # 紫色
        '齐司礼': '#87CEFA',      # 浅蓝色
        '骨灰': '#FFA500',        # 橙色
        '光与夜之恋陆沉': '#8B0000' # 深红色
    }

    # 3. 截取最近的 24 小时数据 (每小时7个角色，7*24 = 168 行数据)
    recent_df = df.tail(168).copy()

    st.subheader("🏆 过去 24 小时排名变动 (1 为最高)")

    # 4. 使用高级工具 Plotly 画图
    fig = px.line(
        recent_df, 
        x='时间', 
        y='排名', 
        color='显示名称',
        color_discrete_map=color_mapping,
        markers=True, 
        title="超话排名走势图"
    )

    # 核心技术点：强行翻转 Y 轴！并强制只显示 1 到 7 的整数
    fig.update_layout(
        yaxis=dict(
            autorange="reversed",  # 翻转！1 在最上面
            tickmode='linear', 
            tick0=1, 
            dtick=1                # 刻度间隔为 1
        ),
        xaxis_title="抓取时间",
        yaxis_title="排名 (Top 1-7)",
        hovermode="x unified"      # 鼠标放上去可以同时对比所有人的排名
    )

    # 在网页上渲染图表
    st.plotly_chart(fig, use_container_width=True)

    # 底部留一个硬核数据表
    st.subheader("📊 最新一小时快照")
    latest_time = df['时间'].max()
    latest_df = df[df['时间'] == latest_time].sort_values(by='排名')
    # 只展示大家关心的列
    st.dataframe(latest_df[['排名', '显示名称', '今日互动', '粉丝数']], use_container_width=True)

else:
    st.warning("🔄 暂未读取到数据，请等待 GitHub 爬虫机器人运行...")
