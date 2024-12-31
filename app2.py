import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from pyecharts.charts import WordCloud, Bar, Pie, Line, Funnel, Radar, Scatter
import re
import string
import pandas as pd


# 函数用于从指定URL获取文本内容，并进行初步清理（移除标点符号、多余的空白字符等）
def get_text_from_url(url):
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()

        # 移除文本中的标点符号
        text = text.translate(str.maketrans("", "", string.punctuation))
        # 将所有多余的空白字符替换为单个空格，并去除首尾空白
        text = re.sub(r'\s+', ' ', text).strip()

        return text
    except requests.RequestException as e:
        print(f"请求出错: {e}")
        return ""


# 对给定的文本进行分词，并统计出现频率最高的前top_n个词语
def word_frequency(text, top_n=20):
    words = [word for word in jieba.cut(text) if len(word) >= 2 and word.strip()]
    word_counts = Counter(words)
    return word_counts.most_common(top_n)


# Streamlit界面配置，允许用户选择图表类型和使用的库
st.sidebar.title("图表选择")
selected_chart = st.sidebar.selectbox("请选择图表类型", ["词云图", "柱状图", "饼图"])
selected_library = st.sidebar.selectbox("请选择可视化库", ["Pyecharts", "Plotly", "Altair"])

# 用户输入文章URL
url = st.text_input("请输入文章URL:")
if url:
    text = get_text_from_url(url)
    # 显示抓取的文本
    st.subheader("抓取的文本内容")
    st.text_area("文本内容", value=text, height=300)  # 使用text_area显示文本，并设置高度
    
    word_counts = word_frequency(text)

    # 用户可以选择过滤低频词
    min_count = st.sidebar.slider("过滤低频词（词频大于等于）", min_value=1, max_value=10, value=1)
    filtered_word_counts = [(word, count) for word, count in word_counts if count >= min_count]

    words, counts = zip(*filtered_word_counts)
    df = pd.DataFrame({'words': words, 'counts': counts})

    # 根据用户选择绘制相应的图表并使用选定的库
    if selected_library == "Plotly":
        import plotly.express as px

        if selected_chart == "词云图":
            fig = px.scatter(df, x='words', y='counts', size='counts', hover_data=['words'])
        elif selected_chart == "柱状图":
            fig = px.bar(df, x='words', y='counts')
        elif selected_chart == "饼图":
            fig = px.pie(df, names='words', values='counts')

        st.plotly_chart(fig)

    elif selected_library == "Altair":
        import altair as alt

        if selected_chart == "词云图":
            chart = alt.Chart(df).mark_circle().encode(
                alt.X('words:N'),
                alt.Y('counts:Q'),
                size='counts',
                tooltip=['words']
            )
        elif selected_chart == "柱状图":
            chart = alt.Chart(df).mark_bar().encode(
                x='words:N',
                y='counts:Q'
            )
        elif selected_chart == "饼图":
            chart = alt.Chart(df).mark_arc().encode(
                theta='counts:Q',
                color='words:N'
            )

        st.altair_chart(chart, use_container_width=True)

    elif selected_library == "Pyecharts":
        if selected_chart == "词云图":
            wordcloud = WordCloud()
            data = [(word, count) for word, count in filtered_word_counts]
            wordcloud.add("", data)
            st.components.v1.html(wordcloud.render_embed(), height=600)

        elif selected_chart == "柱状图":
            bar = Bar()
            bar.add_xaxis(list(words))
            bar.add_yaxis("词频", list(counts))
            st.components.v1.html(bar.render_embed(), height=400)

        elif selected_chart == "饼图":
            pie = Pie()
            pie.add("", [list(z) for z in zip(words, counts)])
            st.components.v1.html(pie.render_embed(), height=400)