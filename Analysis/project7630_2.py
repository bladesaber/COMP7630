#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 17:10:27 2020

@author: fengyuzou
"""

import sqlite3
import pandas as pd
import numpy as np
import csv
from sklearn import feature_extraction  
from sklearn.feature_extraction.text import TfidfTransformer 
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import linear_kernel 

database = sqlite3.connect('data.db')

#找出用户评分最高的一个电影，评分不能低于0.6
highestRating = {}
rating = csv.reader(open('userRating.csv',encoding='utf-8'))
for row in rating:
    if row[0].split("|")[2] in highestRating:
        if len(row[0].split("|")) == 4 and row[0].split("|")[3] != "" and float(row[0].split("|")[3]) > float(highestRating[row[0].split("|")[2]].split("-")[0]):
            highestRating[row[0].split("|")[2]] = row[0].split("|")[3] + "-" + row[0].split("|")[1]
    else:
        if len(row[0].split("|")) == 4 and row[0].split("|")[3] != "":
            highestRating[row[0].split("|")[2]] = row[0].split("|")[3] + "-" + row[0].split("|")[1]
container = []

#去除低分的
for (k,v) in  highestRating.items():
    if float(v.split("-")[0]) > 6.0:
        li = []
        li.append(k)
        li.append(v)
        container.append(li)

test = container[2]
print(test)

keyword = pd.read_sql('select tid,keyword from keyword where tid = "' + test[1].split("-")[1] + '"',database)
genres = pd.read_sql('select tid,Genres from  movie where tid = "' + test[1].split("-")[1] + '"',database)
keywordli = keyword['keyword'].values.tolist()[0].split("|")
genresli = genres['Genres'].values.tolist()[0].split("|")
print(genresli)


#只取一条
summary = pd.read_sql('Select tid,summary from summary group by tid',database)
allSummary = summary['summary'].tolist()
alltid = summary['tid'].tolist()
newSummary = []
stoplist = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"] 
for summary in allSummary:
    cleanStopSummary = [word for word in summary.split() if word not in stoplist]
    newSummary.append(" ".join(cleanStopSummary))
    
simli = []
result = []
w = []

#找出每个词条最高相似率的结果，相似率不能小于0.5
for i in keywordli[0:30]:
    newSummary.append(i)
    vectorizer = CountVectorizer()
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(vectorizer.fit_transform(newSummary))
    word = vectorizer.get_feature_names()
    weight = tfidf.toarray()

    cosineSimilarities = linear_kernel(tfidf[-1:],tfidf).flatten()
    top = sorted(cosineSimilarities)[-2:-1]
    topOneindex = np.argsort(cosineSimilarities)[-2:-1]
    simli.append(top[0])
    if top[0] > 0.5:
        w.append(i)
        result.append(topOneindex[0])
    newSummary.pop()

        
print(result)
print(simli)
print(w)

#推荐的电影类型必须和用户高分电影有重叠
tids=[]
summaryContainer = []
for item in result: 
    print(item)
    types = pd.read_sql('select tid,Genres from  movie where tid = "' + alltid[item] + '"',database)
    typesli = types['Genres'].values.tolist()[0].split("|")
    print(typesli)
    for i in typesli:
        for j in genresli:
            if i == j:      
                tids.append(alltid[item])
                summaryContainer.append(allSummary[item])
      
    
movie = pd.read_sql('select tid,title from movie',database)
recommendMovie = []
for items in tids:
    recommendMovie.append(movie[["tid","title"]][movie["tid"] == items]["title"].tolist()[0])
finalResult = dict(zip(recommendMovie,summaryContainer))
print(finalResult)


    



