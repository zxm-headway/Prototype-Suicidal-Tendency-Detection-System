import json
import re
import jieba
import pandas as pd
from collections import Counter
from snownlp import SnowNLP
from model.detect import *


def remove_punctuation(text):
    clean_text = re.sub(r'[^\w\s]', '', text)
    return clean_text


def add_words_jieba():
    file_path = os.path.join(os.path.dirname(__file__), '中文自杀词典.xlsx')
    words_df = pd.read_excel(file_path, engine='openpyxl')
    words_list = words_df['WORD'].tolist()
    for word in words_list:
        if not isinstance(word, str):
            word = str(word)
        jieba.add_word(word)


def clean_text(text):
    cleaned_text = re.sub(r'\s*([，。！？：；‘’“”、,\.!?;:])\s*', r'\1', text)
    cleaned_text = cleaned_text.replace(" ", "")
    cleaned_text = re.sub(r'#.*?#', '', cleaned_text)
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    cleaned_text = re.sub(url_pattern, '', cleaned_text)
    mention_pattern = r'@[^ \t\n\r\f\v，。；：？！、]*'
    cleaned_text = re.sub(mention_pattern, '', cleaned_text)
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F"  # 表情符号
        "\U0001F300-\U0001F5FF"  # 符号和图形
        "\U0001F680-\U0001F6FF"  # 交通工具
        "\U0001F700-\U0001F77F"  # 化学符号
        "\U0001F780-\U0001F7FF"  # 几何图案
        "\U0001F800-\U0001F8FF"  # 补充箭头-C
        "\U0001F900-\U0001F9FF"  # 补充箭头-D
        "\U0001FA00-\U0001FA6F"  # 补充箭头-E
        "\U0001FA70-\U0001FAFF"  # 象形文字
        "\U00002600-\U000027BF"  # 杂项符号
        "\U0001F1E6-\U0001F1FF"  # 区域标志
        "]+", flags=re.UNICODE)
    cleaned_text = emoji_pattern.sub(r'', cleaned_text)
    return cleaned_text


def get_emotions_wave(sentence_list):
    emotions_wave_list = []
    for post in sentence_list:
        s = SnowNLP(post)
        emotions_wave_list.append(s.sentiments)
    return emotions_wave_list


def preprocess_emtions(sentence_list):
    p_n_num = []
    for word in sentence_list:
        s = SnowNLP(word)
        sentiment = s.sentiments
        if sentiment > 0.7:
            p_n_num.append(2)
        elif sentiment < 0.3:
            p_n_num.append(0)
        else:
            p_n_num.append(1)
    return p_n_num


def preprocess_text(text):
    words = jieba.cut(text)
    segmented_text = " ".join(words)
    processed_text = re.sub(r'[^\u4e00-\u9fa5\s]', '', segmented_text)
    return processed_text.split()


async def preprocess_words(sentence_list):
    context = []
    emotions = preprocess_emtions(sentence_list)
    emotions_count = Counter(emotions)
    for post in sentence_list:
        context.extend(preprocess_text(post))
    word_counts = Counter(context)
    most_common_words = word_counts.most_common(50)
    return most_common_words, emotions_count


async def pre_textData(posts):
    context = []
    add_words_jieba()
    for post in posts:
        post = clean_text(post)
        content = remove_punctuation(post)
        content = jieba.lcut(content, cut_all=False)
        content = " ".join(content)
        if content != '\n' or content != '' or content != ' ':
            context.append(content.strip().split(' '))
    file_path = os.path.join(os.path.dirname(__file__), 'words_id.json')
    with open(file_path, "r", encoding="utf-8") as file:
        loaded_word_dict = json.load(file)
    res = main(loaded_word_dict, context)
    return res.item()


async def posts_emtions(posts):
    res = preprocess_emtions(posts)
    emotion_num = Counter(res)
    pos = emotion_num[2]
    mod = emotion_num[1]
    neg = emotion_num[0]
    emtion_dict = {
        '正向': pos,
        '中性': mod,
        '负面': neg,
    }
    return emtion_dict