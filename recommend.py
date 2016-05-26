# -*- coding: utf-8 -*-
"""
根据用户的查询需求，推荐最相关的十本书
注意用户查询的词必须包含在提取的关键词中
"""

import os
import sys
import codecs
import sys
import jieba

reload(sys)
sys.setdefaultencoding('utf-8')
abspath = os.getcwd()

def read_data(txtPath, coding = 'utf-8'):
        '''读取关键词数据，第一列是图书ID，后面是20个关键词'''
        f = codecs.open(txtPath,'r',coding).readlines()
        data = []
        for line in f:
            line = line.replace("\r\n","")
            line = line.replace("\n","")
            line = line.split(',')
            data.append(line)
        return data

def book_name(rec_id):
    '''book_Name_ID.txt中的第一列是图书名，第二列是图书ID。
    根据content_based得到图书ID，从book_Name_ID.txt中找到对应的书名，推荐给读者'''
    result = []
    data = read_data(abspath + '\\dataset\\book_Name_ID.txt')
    for j in range(len(rec_id)):
        for i in range(len(data)):
            if rec_id[j] == data[i][1]:
                result.append(data[i][0])
    return result

def content_based(data, keyword):
    '''基于内容的推荐，将关键词抽取步骤中得到的关键词的tfidf值以及关键词在语义中的权重分别作为关键词与图书之间的相似度,
    用户输入查询需求之后，得到一组查询关键词，如果该查询词等于某个关键词，则记录关键词对应的图书ID和相似度值，
    再根据相似度的大小对图书ID进行排序，最后按顺序找到图书ID对应的图书名，给出推荐结果。最后至少会给出一个推荐结果。
    数据的第一列为图书ID，第二列是关键词，第三列是关键词对应的相似度，后面每两列是一组，以此类推'''
    
    '''如果有多个查询关键词，先找同时匹配这些查询关键词的图书，按照相似度大小进行排列，
    然后再找单独匹配每个查询关键词的图书，按照相似度大小进行排列，
    最后将上面两步得到的图书放在一起作为推荐结果，第一步得到的图书排在前面'''
    
    result1 = []
    if len(keyword) > 1: # keyword是一组关键词
        for i in range(len(data)):
            line = data[i]
            count = 0
            for k in range(len(keyword)):
                if keyword[k] in line:
                    count += 1
            if count == len(keyword):
                temp = []
                temp.append(line[0])   # line[0]是图书ID
                w = 0
                for k in range(len(keyword)):
                    for j in range(1,len(line),2):
                        if keyword[k] == line[j]:
                            # 对于多个关键词，将相似度相加作为总的相似度
                            w += float(line[j+1])   # line[j+1]是相似度
                temp.append(str(line[j+1]))
                result1.append(temp)
    #将结果按照相似度从大到小的顺序进行排列
    result1.sort(key=lambda x:float(x[1]),reverse=True)
    
    result2 = []
    for k in range(len(keyword)):
        word = keyword[k]
        for i in range(len(data)):
            line = data[i]
            temp = []
            for j in range(1,len(line),2):
                flag = ''
                for i in range(len(result1)):
                    if line[0] in result1[i]:   # line[0]是图书ID
                        flag = 'repeat'   # 如果flag==‘repeat’，说明该图书在result1中已经出现了，此处不再重复考虑
                if (word == line[j]) and (flag == ''):
                    temp.append(line[0])   # line[0]是图书ID
                    temp.append(str(line[j+1]))   # line[j+1]是相似度
                    result2.append(temp)
                    break
    #将结果按照相似度从大到小的顺序进行排列
    result2.sort(key=lambda x:float(x[1]),reverse=True)
    
    result_id = result1
    for i in range(len(result2)):
        result_id.append(result2[i])
    book_id = []
    for i in range(len(result_id)):
        book_id.append(result_id[i][0])
    result_book = book_name(book_id)
    return result_book
    

def apriori_based(data, keyword):
    '''基于Apriori的推荐，也就是基于关联规则的推荐，我们假定用户每次给出一个查询词，（该查询词必须包含在抽取出的关键词中），
    那么只需要找到和该查询词一起出现的图书即可，因为一本图书对应的关键词都是唯一的，所以这里只要用户查询的关键词和图书一起出现就可以进行推荐。
    也就是将关键词作为关联规则的前项，图书名作为关联规则的后项，如果关键词和图书名一起出现，则当用户查询该关键词时，将对应的图书推荐给用户。
    推荐结果可以按照图书的热门程度进行排序，豆瓣上Top250图书的顺序就是按照热门程度进行排序的，也就是原始数据中图书所对应的序号，
    序号越小的图书热门程度越高，在推荐结果中的顺序越靠前.
    数据的第一列是图书的序号，第二列是图书名，第三列及以后是20个关键词'''
    
    '''如果有多个查询关键词，先找同时匹配这些查询关键词的图书，按照热门程度进行排列，
    然后再找单独匹配每个查询关键词的图书，按照热门程度大小进行排列，
    最后将上面两步得到的图书放在一起作为推荐结果，第一步得到的图书排在前面'''
    
    if data[0][0] == codecs.BOM_UTF8 or u'\ufeff1':
        data[0][0] = '1'
    
    result1 = []
    if len(keyword) > 1: # keyword是一组关键词
        for i in range(len(data)):
            line = data[i]
            count = 0
            for k in range(len(keyword)):
                if keyword[k] in line:
                    count += 1
            if count == len(keyword):
                temp = []
                temp.append(line[1])   # line[1]是图书ID
                w = 0
                for k in range(len(keyword)):
                    for j in range(2,len(line)):
                        if keyword[k] == line[j]:
                            w += int(line[0])   # line[0]是热门度
                temp.append(str(w))
                result1.append(temp)
    #将结果按照热门程度从大到小的顺序进行排列
    result1.sort(key=lambda x:int(x[1]))
    #print result1
    result2 = []
    for k in range(len(keyword)):
        word = keyword[k]
        for i in range(len(data)):
            line = data[i]
            temp = []
            for j in range(2,len(line)):
                flag = ''
                for i in range(len(result1)):
                    if line[1] in result1[i]:    # line[1]是图书ID
                        flag = 'repeat'   # 如果flag==‘repeat’，说明该图书在result1中已经出现了，此处不再重复考虑
                if (word == line[j]) and (flag == ''):
                    temp.append(line[1])
                    temp.append(line[0])   # line[0]是热门度
                    result2.append(temp)
                    break
    #将结果按照图书的热度从大到小的顺序进行排列，即按照图书序号从小到大的顺序进行排列
    result2.sort(key=lambda x:int(x[1]))
    #print result2
    result = result1
    for i in range(len(result2)):
        result.append(result2[i])
    
    result_book = []
    for i in range(len(result)):
        result_book.append(result[i][0])
    return result_book

def output(dataset, Path, coding='utf-8'):
    '''输出'''
    f = open(Path, "w")
    for i in range(len(dataset)):
        f.write(dataset[i]+'\n')
    f.close()

def qury(s):
    '''检查用户输入的关键词，是否同时包含在两种方法找到的关键词表之中.
    首先将查询字符串s进行分词得到一组查询关键词word'''
    word1 = jieba.cut(s, cut_all=True)
    word = []
    for item in word1:
        word.append(item)
    '''然后分别检查每一个关键词是否在两个关键词表中,如果在则分别放入result1和result2中'''
    result1 = []
    result2 = []
    keywords1 = codecs.open(abspath + '\\dataset\\keywords_tfidf.txt','r','utf-8').readlines()
    keywords2 = codecs.open(abspath + '\\dataset\\keywords_textrank.txt','r','utf-8').readlines()
    for j in range(len(word)):
        for i in xrange(len(keywords1)):
            temp = keywords1[i].split(',')
            for k in range(len(temp)):
                if word[j] == temp[k] and (word[j] not in result1):
                    result1.append(word[j])
    for j in range(len(word)):
        for i in xrange(len(keywords2)):
            temp = keywords2[i].split(',')
            for k in range(len(temp)):
                if word[j] == temp[k] and (word[j] not in result2):
                    result2.append(word[j])
    '''最后将result1和result2中共有的关键词写入result，如果没有则result为空'''
    result = []
    if (len(result1) != 0) and (len(result2) != 0):
        result = [x for x in result2 if x in result1]
    return result

if __name__=='__main__':
    data1 = read_data(abspath + '\\dataset\\tfidf_content.txt')
    data2 = read_data(abspath + '\\dataset\\textrank_content.txt')
    data3 = read_data(abspath + '\\dataset\\tfidf_apriori.txt')
    data4 = read_data(abspath + '\\dataset\\textrank_apriori.txt')
    
    '''用户输入的关键词，必须同时包含在两种方法找到的关键词之中，否则将返回‘没有查找到相关图书，请重新输入’
    四组结果会分别写入rec1.txt、rec2.txt、rec3.txt、rec4.txt中'''
    keyword = '什么童话书比较经典'   #经典, 童话, 小说
    #keyword = '你说什么'
    result = qury(keyword)
    if len(result) == 0:
        print "没有查找到相关图书，请重新输入"
    else:
        keyword = result
        '''基于TFIDF的关键词抽取 + 基于内容的推荐'''
        rec1 = content_based(data1, keyword)
        #print rec1
        output(rec1, abspath + '\\rec1.txt')
        
        '''基于语义的关键词抽取 + 基于内容的推荐'''
        rec2 = content_based(data2, keyword)
        #print rec2
        output(rec2, abspath + '\\rec2.txt')
        
        '''基于TFIDF的关键词抽取 + 基于Apriori算法的推荐'''
        rec3 = apriori_based(data3, keyword)
        #print rec3
        output(rec3, abspath + '\\rec3.txt')
        
        '''基于语义的关键词抽取 + 基于Apriori算法的推荐'''
        rec4 = apriori_based(data4, keyword)
        #print rec4
        output(rec4, abspath + '\\rec4.txt')


