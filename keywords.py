#coding:utf-8
'''关键词抽取，分别使用基于TFIDF的方法和基于语义的方法进行关键词抽取'''
import os
import sys
import codecs
import jieba
import jieba.analyse

reload(sys)
sys.setdefaultencoding('utf-8')
abspath = os.getcwd()

class preprocess(object):
    """预处理"""
    def __init__(self):
        pass
    def read_txt(self, txtPath, coding = 'utf-8'):
        '''读取评论数据，dataset.txt中第一列是评论文本，第二列是图书ID，
        去除回车、制表符之后，将其分成两列，存入dataset中'''
        #import codecs
        f = codecs.open(txtPath,'r',coding).readlines()
        f[0] = f[0].replace(u"\ufeff",u"")
        dataset = []
        for line in f:
            line = line.replace("\r\n","")
            line = line.replace("\n","")
            line = line.split('\t')
            dataset.append(line)
        return dataset

    def read_txt2(self, txtPath, coding = 'utf-8'):
        '''读取评论数据，dataset.txt中第一列是评论文本，第二列是图书ID，
        去除回车、制表符之后，直接存入dataset中'''
        #import codecs
        f = codecs.open(txtPath,'r',coding).readlines()
        f[0] = f[0].replace(u"\ufeff",u"")
        dataset = []
        for line in f:
            line = line.replace("\r\n","")
            line = line.replace("\n","")
            dataset.append(line)
        return dataset

    def transtxt(self, txtPath, coding = 'utf-8'):
        '''将评论数据按照图书ID进行分类，按字典格式进行存储，
        字典的key是图书的ID，value是一个数组，包含该图书ID对应的所有评论'''
        dataset = self.read_txt(txtPath)
        
        bookContent = {}
        bookId = []
        for i in range(len(dataset)):
            if len(dataset[i]) != 2:
                print dataset[i]
            else:
                bookId.append(dataset[i][1])
                if dataset[i][1] not in bookContent:
                    bookContent[dataset[i][1]] = [dataset[i][0]]
                else:
                    temp = bookContent[dataset[i][1]]
                    temp.append(dataset[i][0])
                    bookContent[dataset[i][1]] = temp
        bookId = list(set(bookId))
        return bookId,bookContent

    def writeMatrix(self, dataset, Path, coding = "utf-8"):
        '''将图书ID及对应的20个关键词输出'''
        for i in xrange(len(dataset)):
            temp = dataset[i]
            temp = [str(temp[j]) for j in xrange(len(temp))]
            temp = ",".join(temp)
            dataset[i] = temp
        string = "\n".join(dataset)
        f = open(Path, "w")
        f.write(string+"\n")
        f.close()

    def cutWords(self, dataset, stop_words_path="None"):
        #分词/去停用词
        result = []
        if stop_words_path == "None":
            for i in xrange(len(dataset)):
                temp = " ".join(jieba.cut(dataset[i]))
                result.append(temp)
            return result
        else:
            stop_words = self.read_txt2(stop_words_path)
            # print stop_words
            for i in xrange(len(dataset)):
                tup = []
                temp = " ".join(jieba.cut(dataset[i]))
                temp = temp.split()
                # print temp
                if len(temp) != 0:
                    for j in range(len(temp)):
                        # print j
                        # print stop_words
                        if temp[j] not in stop_words:
                            tup.append(temp[j])
                tup = " ".join(tup)
                result.append(tup)
                break
            return result

    def count(self, dataset):
        #计数
        count = {}
        for i in dataset:
            if i in count:
                count[i] += 1
            else:
                count[i] =1
        return count

def fix(words):
    '''如果找到的25个关键词中含有特殊'...'或'&#'，则将其剔除，然后返回前20个关键词'''
    drop = ['..','...','.....','......','&#']
    result = []
    result.append(words[0])
    for i in range(1,len(words)):
        if words[i][0] not in drop:
            result.extend(words[i])
    return result[0:41]

def tfidf_feature():
    '''jieba.analyse.extract_tags(s, topK=22)可以直接对文本进行分词、去停用词处理，
    并根据tfidf值的大小，给出排在前20的关键词。注，jieba有内置的idf语料库和stopwords语料库'''
    bookId,bookContent = preprocess().transtxt(abspath+'\\dataset\\dataset.txt')
    result = []
    for i in range(len(bookId)):
        temp = [bookId[i]]
        s = ','.join(bookContent[bookId[i]])
        '''输出图书ID，以及对应的前25个关键词和tfidf值。
        对于含有特殊字符的关键词，使用上面定义的fix()函数进行剔除，最后保留前20个关键词'''
        words = jieba.analyse.extract_tags(s, topK=25, withWeight=True, allowPOS=())
        for j in range(len(words)):
            temp.append(words[j])
        print temp
        temp = fix(temp)
        result.append(temp)
    '''将结果写入tfidf.txt中'''
    preprocess().writeMatrix(result,'tfidf.txt')    

def textrank_feature():
    '''jieba.analyse..textrank(s, withWeight=True)可以直接对文本进行分词、去停用词处理，
    并根据每个词在词网络中权值的大小，给出排在前20的关键词。注，jieba有内置的语料库和stopwords语料库'''
    bookId,bookContent = preprocess().transtxt(abspath+'\\dataset\\dataset.txt')
    result = []
    for i in range(len(bookId)):
    	temp = [bookId[i]]
        s = ','.join(bookContent[bookId[i]])
        '''输出基于语义的关键词x和对应的权重w'''
        for x, w in jieba.analyse.textrank(s, withWeight=True):
            #print('%s %s' % (x, w))
            temp.extend((x,w))
        print temp
        result.append(temp)
    '''将结果写入textrank.txt中'''
    preprocess().writeMatrix(result,'textrank.txt')

if __name__=='__main__':
    tfidf_feature()
    textrank_feature()
