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
site.addsitedir('/bos/usr0/cx/PyCode/TermLevelDiversification')
site.addsitedir('/bos/usr0/cx/PyCode/cxPyLib')
import os
from cxBase.base import cxBaseC
#from cxBase.Conf import cxConfC
from IndriRelate.IndriPackedRes import *
from IndriRelate.IndriInferencer import *
from cxBase.TextBase import TextBaseC
from cxBase.Vector import VectorC
# from Reranking.DocTopicDistributionCalculate import DocTopicDistributionCalculatorC


class DiversifiedRerankC(cxBaseC):
    
    def Init(self):
        cxBaseC.Init(self)
        self.DataDir = ""
        self.QIn = ""
        self.CacheDir = ""
        self.TopDocN = 100
        self.Lambda = 0.5
        self.NumOfSt = 0
        self.DocProbNamePre = ""
        self.OutName = ""
        
        
    @staticmethod
    def ShowConf():
        cxBaseC.ShowConf()
        print "datadir\nin\nout\ncachedir\ntopdocn\nlambda\ndocprobpre"
        
    def SetConf(self, ConfIn):
        cxBaseC.SetConf(self, ConfIn)
        self.DataDir = self.conf.GetConf('datadir') + '/'
        self.QIn = self.conf.GetConf('in')
        self.OutName = self.conf.GetConf('out')
        self.CacheDir = self.conf.GetConf('cachedir') + '/'
        self.TopDocN = int(self.conf.GetConf('topdocn'))
        self.Lambda = float(self.conf.GetConf('lambda', self.Lambda))
        self.DocProbNamePre = self.conf.GetConf('docprobpre')
    
    
    def Process(self):
        out = open(self.OutName,'w')
        for line in open(self.QIn):
            qid,query = line.strip().split('\t')
            qid = int(qid)
            lDocNo,lDocScore = self.ProcessOneQ(qid, query)
            for i in range(len(lDocNo)):
                print >> out,"%d Q0 %s %d %f div" %(qid,lDocNo[i],i + 1,lDocScore[i])
            print "[%d][%s] ranked" %(qid,query)
        out.close()     
        return
    
    
        
    def ProcessOneQ(self,qid,query):
        lDoc = ReadPackedIndriRes(self.CacheDir + query, self.TopDocN)
        lDocNo = [doc.DocNo for doc in lDoc]        
        lDocProbVec = self.ReadDocProbVec(lDocNo, qid)        
        lReRankedDocNo,lDocScore = self.RerankForOneQ(qid,query,lDoc,lDocProbVec)        
        return lReRankedDocNo,lDocScore
            
    def ReadDocProbVec(self,lDocNo,qid):
        lDocProbVec = [VectorC()] * len(lDocNo)
        for line in open(self.DataDir + '%d_%s_DocTopicProb' %(qid,self.DocProbNamePre)):
            DocNo,VecStr = line.strip().split('\t')
            Vector = VectorC()
            Vector.loads(VecStr)
            p = lDocNo.index(DocNo)
            lDocProbVec[p] = Vector   
        return lDocProbVec

    def RerankForOneQ(self,qid,query,lDoc,lDocProbVec):
        '''
        API used to rerank documents.
        to be implemented by subclass: xQuAd, PM-2
        '''
        print 'call my sub class'
        