import os
# import pandas as pd
import fasttext
import jieba
import numpy as np
from django.http import JsonResponse
import pymssql
# from sklearn.utils import shuffle

base_path = os.path.dirname(os.getcwd()) + "/files"
print(base_path)
# def train_model():
#     # ”“”训练词向量模型并保存“”“
#     model = fasttext.train_unsupervised(base_path + '\\result.txt', model='cbow')
#     model.save_model("news_fasttext.model.bin")


# def get_word_vector(word):
#     # ”“”获取某词词向量“”“
#     print(os.path.dirname(os.getcwd()) + '/models/news_fasttext.model.bin')
#     model = fasttext.load_model(os.path.dirname(os.getcwd()) + '/easymoney_crawler/models/news_fasttext.model.bin')
#     word_vector = model.get_word_vector(word)
#     return word_vector


def get_sentence_vector(sentence):
    # ”“”获取某句句向量“”“
    cut_words, sentence_vector = jieba.lcut(sentence.strip().replace("\t", "").replace("\n", "")), None
    model = fasttext.load_model(os.path.dirname(os.getcwd()) + '/easymoney_crawler/models/news_fasttext.model.bin')
    for word in cut_words:
        word_vector = model.get_word_vector(word)
        if sentence_vector is not None:
            sentence_vector += word_vector
        else:
            sentence_vector = word_vector

    sentence_vector = sentence_vector / len(cut_words)
    return sentence_vector


def cos_sim(vector_a, vector_b):
    # 计算两个向量之间的余弦相似度
    # :param vector_a: 向量 a
    # :param vector_b: 向量 b
    # :return: sim
    vector_a, vector_b = np.mat(vector_a), np.mat(vector_b)
    num = float(vector_a * vector_b.T)
    denom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    cos = num / denom
    sim = 0.5 + 0.5 * cos
    return sim


def get_similarity(request):
    text1, text2 = request.GET["Text1"], request.GET["Text2"]
    return JsonResponse({"code": 200, "data": cos_sim(get_sentence_vector(text1), get_sentence_vector(text2))}, safe=False)


# def get_similarity(request):
#     final_result, datas = {}, get_alldata()
#     try:
#         text1 = request.GET['Text']
#         for item in datas:
#             print(cos_sim(get_sentence_vector(text1), get_sentence_vector(datas[item])))
#             final_result[item] = cos_sim(get_sentence_vector(text1), get_sentence_vector(datas[item]))
#         sorted(final_result.items(), key=lambda x: x[1], reverse=True)
#     except Exception:
#         return JsonResponse({"code": 400, "data": "线程炸了"},
#                             safe=False)
#     return JsonResponse({"code": 200, "data": final_result}, safe=False)
#
#
# def get_alldata()->map:
#     conn = pymssql.connect("119.23.221.142:1433", "sa", "Grw19980628", "AIStock")
#     result = {}
#     if conn:
#         print("连接成功！")
#         cursor = conn.cursor()
#         cursor.execute("select Id, Question from Knowledges")
#         rows = cursor.fetchall()
#         for row in rows:
#             print(row)
#             result[row[0]] = str(row[1]).strip().replace("\r", "").replace("\n", "")
#     return result




