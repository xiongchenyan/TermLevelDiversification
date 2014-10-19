'''
Created on Oct 19, 2014 7:06:32 PM
@author: cx

what I do:
I am the base class for diversification reranking systems
what's my input:
p(topic|doc)
doc - relevance ranking score

what's my output:
a new rank of document

'''


import site

site.addsitedir('/bos/usr0/cx/PyCode/cxPyLib')
import os
from cxBase.base import cxBaseC
#from cxBase.Conf import cxConfC
from IndriRelate.IndriPackedRes import *
from IndriRelate.IndriInferencer import *
from cxBase.TextBase import TextBaseC
from cxBase.Vector import VectorC
from Reranking.DocTopicDistributionCalculate import DocTopicDistributionCalculatorC


class DiversifiedRerankC(cxBaseC):
    
    def Init(self):
        cxBaseC.Init(self)
        self.DataDir = ""
        self.QIn = ""
        self.CacheDir = ""
        self.TopDocN = 100
        
        
    @staticmethod
    def ShowConf():
        cxBaseC.ShowConf()
        print "datadir\nin\ncachedir\ntopdocn"
        
    def SetConf(self, ConfIn):
        cxBaseC.SetConf(self, ConfIn)
        self.DataDir = self.conf.GetConf('datadir') + '/'
        self.QIn = self.conf.GetConf('qin')
        self.CacheDir = self.conf.GetConf('cachedir') + '/'
        self.TopDocN = self.conf.GetConf('topdocn')
        
        
    def ProcessOneQ(self,qid,query):
        lDoc = ReadPackedIndriRes(self.CacheDir + query, self.TopDocN)
        lDocNo = [doc.DocNo for doc in lDoc]        
        lDocProbVec = self.ReadDocProbVec(lDocNo, qid)        
        lReRankedDocNo = self.RerankForOneQ(qid,query,lDoc,lDocProbVec)        
        return lReRankedDocNo
            
    def ReadDocProbVec(self,lDocNo,qid):
        lDocProbVec = [] * len(lDocNo)
        for line in open(self.DataDir + '%d_DocTopicProb' %(qid)):
            DocNo,VecStr = line.strip().split('\t')
            Vector = VectorC()
            Vector.loads(VecStr)
            p = lDocNo.Index(DocNo)
            lDocProbVec[p] = Vector   
        return lDocProbVec

    def RerankForOneQ(self,qid,query,lDoc,lDocProbVec):
        '''
        API used to rerank documents.
        to be implemented by subclass: xQuAd, PM-2
        '''
        print 'call my sub class'
