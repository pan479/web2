import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from pyecharts.charts import WordCloud, Bar, Pie
import re
import string
import pandas as pd
import matplotlib.pyplot as plt

# 函数用于从指定URL获取文本内容，并进行初步清理（移除标点符号、多余的空白字符等）
def get_text_from_url(url):
    try:
        response = requests.get(url)  # 发送GET请求以获取网页内容
        response.encoding = 'utf-8'  # 设置响应编码为UTF-8
        response.raise_for_status()  # 如果请求失败，则抛出异常
        soup = BeautifulSoup(response.text, 'html.parser')  # 使用BeautifulSoup解析HTML文档
        text = soup.get_text()  # 获取纯文本内容

        # 移除文本中的标点符号
        text = text.translate(str.maketrans("", "", string.punctuation))
        # 将所有多余的空白字符替换为单个空格，并去除首尾空白
        text = re.sub(r'\s+', ' ', text).strip()

        return text  # 返回清理后的文本
    except requests.RequestException as e:  # 捕获网络请求异常
        print(f"请求出错: {e}")
        return ""  # 请求失败时返回空字符串

# 对给定的文本进行分词，并统计出现频率最高的前top_n个词语
def word_frequency(text, top_n=20):
    words = [word for word in jieba.cut(text) if len(word) >= 2 and word.strip()]  # 分词并过滤掉长度小于2的词及空白字符
    word_counts = Counter(words)  # 统计每个词出现的次数
    return word_counts.most_common(top_n)  # 返回最频繁出现的top_n个词及其频次

# Streamlit界面配置，允许用户选择图表类型和使用的库
st.sidebar.title("图表选择")
selected_chart = st.sidebar.selectbox("请选择图表类型", ["词云图", "柱状图", "饼图"])
selected_library = st.sidebar.selectbox("请选择可视化库", ["Pyecharts", "Matplotlib", "Plotly"])

# 用户输入文章URL
url = st.text_input("请输入文章URL:")
if url:
    text = get_text_from_url(url)  # 调用函数获取并清理文本内容


    st.subheader("抓取的文本内容")
    st.text_area("文本内容", value=text, height=300)  # 使用text_area显示文本，并设置高度

    word_counts = word_frequency(text)  # 对文本进行分词并统计词频
    # 用户可以选择过滤低频词
    min_count = st.sidebar.slider("过滤低频词（词频大于等于）", min_value=1, max_value=10, value=1)
    filtered_word_counts = [(word, count) for word, count in word_counts if count >= min_count]

    words, counts = zip(*filtered_word_counts)
    df = pd.DataFrame({'words': words, 'counts': counts})

    # 根据用户选择绘制相应的图表并使用选定的库
    if selected_library == "Matplotlib":
        if selected_chart == "柱状图":
            plt.figure(figsize=(10, 8))
            plt.bar(words, counts)
            plt.xlabel('Words')
            plt.ylabel('Counts')
            plt.title('Word Frequency')
            st.pyplot(plt)
        elif selected_chart == "饼图":
            plt.figure(figsize=(8, 8))
            plt.pie(counts, labels=words, autopct='%1.1f%%')
            plt.title('Word Frequency')
            st.pyplot(plt)

    elif selected_library == "Plotly":
        import plotly.express as px  # 动态导入Plotly库

        if selected_chart == "词云图":
            fig = px.scatter(df, x='words', y='counts', size='counts', hover_data=['words'])  # 使用Plotly创建散点图模拟词云图效果
        elif selected_chart == "柱状图":
            fig = px.bar(df, x='words', y='counts')  # 使用Plotly创建柱状图
        elif selected_chart == "饼图":
            fig = px.pie(df, names='words', values='counts')  # 使用Plotly创建饼图

        st.plotly_chart(fig)  # 在Streamlit中展示Plotly图表

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