import os
import numpy as np
import pandas as pd
import streamlit as st
from glob import glob
from PIL import Image
from kiwipiepy import Kiwi
from wordcloud import WordCloud, ImageColorGenerator
from src.plot import plot_count
from src.tags import tags

# init
kiwi = Kiwi()
IMAGE_DIR = "background"
FONT_FILE = "font/NanumGothic.ttf"

# title
st.markdown("# 한국어 텍스트 분석기")

# add user words
userwords = st.sidebar.text_area("추가 단어", value="\n".join(["한국어", "텍스트", "분석기"]))
for userword in userwords.split(): 
    kiwi.add_user_word(userword, "NNP")

# add stop words
stopwords = st.sidebar.text_area("불용어", value="\n".join(["ㅋㅋㅋ", "쿠크르삥뽕"]))
stopwords = stopwords.split()
st.sidebar.markdown("---")


# background image
background_image = st.sidebar.selectbox(
    "배경 이미지",
    [None]+[os.path.split(path)[-1] for path in glob(f"{IMAGE_DIR}/*.png")],
    index=0
)

# tag
tags_selected = st.sidebar.multiselect("품사", options=tags().keys(), default=["일반 명사", "고유 명사"])
tags = [tags()[tag] for tag in tags_selected]

# input
input_text = st.text_area("", value="텍스트를 입력해 주세요.", height=200)

# get tokens
tokens = kiwi.tokenize(input_text)
tokens = [token.form for token in tokens if token.tag in tags and token.form not in stopwords]

# get counts
counts = {}
for token in tokens:
    if token not in counts:
        counts[token] = 1
    else:
        counts[token] += 1
counts = {k: v for k, v in sorted(counts.items(), key=lambda item: item[1], reverse=True)}

# word cloud
if background_image is None:
    mask_image = None
    mask_color = None
else:
    image = Image.open(os.path.join(IMAGE_DIR, background_image))
    mask_image = np.array(image)
    mask_color = ImageColorGenerator(mask_image)

wordcloud = WordCloud(
    font_path=FONT_FILE,  
    background_color="white",
    colormap="Accent_r",            
    max_words=300,
    width=1200,
    height=900,
    random_state=42,
    mask=mask_image,
).generate_from_frequencies(counts)
wordcloud.recolor(color_func=mask_color)

# draw word cloud
st.markdown("### 워드클라우드")
st.image(np.array(wordcloud), use_column_width=True)

# bar graph
length = len(counts.keys())
num = st.sidebar.number_input("빈도수 표기 개수", min_value=1, max_value=length, value=np.minimum(length, 20))
st.sidebar.markdown("---")
fig = plot_count(counts.keys(), counts.values(), num=int(num))

# draw bar chart
st.markdown("### 단어 빈도수")
st.altair_chart(fig, use_container_width=True)

# download csv
df_counts = pd.DataFrame()
df_counts["word"] = counts.keys()
df_counts["count"] = counts.values()
st.download_button(
    label="Download (.csv)",
    data=df_counts.to_csv(index=False).encode("utf-8-sig"),
    file_name=f"count.csv",
    mime="text/csv"
)