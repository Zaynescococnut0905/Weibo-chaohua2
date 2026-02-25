import streamlit as st
import pandas as pd
import plotly.express as px

# === 网页全局设置 ===
st.set_page_config(page_title="超话热度实时看板", page_icon="🔥", layout="wide")
st.title("🔥 游戏角色超话【精准热度】监控 (24h)")

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
    # 1. 代号映射
    name_mapping = {
        '秦彻': '厕', '恋与深空黎深': '黎神', '祁煜': '穆棱',
        '沈星回': '猪', '齐司礼': '齐司礼', '夏以昼': '骨灰',
        '光与夜之恋陆沉': '光与夜之恋陆沉'
    }
    df['显示名称'] = df['角色名'].map(name_mapping).fillna(df['角色名'])

    # 2. 颜色映射
    color_mapping = {
        '厕': '#FF0000', '黎神': '#0000FF', '穆棱': '#FF69B4',
        '猪': '#800080', '齐司礼': '#87CEFA', '骨灰': '#FFA500',
        '光与夜之恋陆沉': '#8B0000'
    }

    # 3. 排名变动图 (1在最上面)
    st.subheader("🏆 排名变动趋势")
    fig_rank = px.line(df.tail(168), x='时间', y='排名', color='显示名称',
                       color_discrete_map=color_mapping, markers=True)
    fig_rank.update_layout(yaxis=dict(autorange="reversed", tickmode='linear', dtick=1))
    st.plotly_chart(fig_rank, use_container_width=True)

    # 4. 精准热度数值图
    st.subheader("📈 精准热度数值走势")
    # 注意这里 values 改成了 '热度值'
    fig_heat = px.line(df.tail(168), x='时间', y='热度值', color='显示名称',
                       color_discrete_map=color_mapping, markers=True)
    st.plotly_chart(fig_heat, use_container_width=True)

    # 5. 最新快照
    st.subheader("📊 实时数据快照")
    latest_df = df[df['时间'] == df['时间'].max()].sort_values(by='排名')
    st.dataframe(latest_df[['排名', '显示名称', '热度值', '粉丝数']], use_container_width=True)

else:
    st.warning("🔄 正在等待 GitHub 机器人同步最新的 App 接口数据...")
