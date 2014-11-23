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
from IndriRelate import IndriInferencer

'''
Nov 16 add function to read the topic term from disk, and calculate the topic probability
not tested
'''


import site
site.addsitedir('/bos/usr0/cx/PyCode/TermLevelDiversification')
site.addsitedir('/bos/usr0/cx/PyCode/cxPyLib')
import os
from cxBase.base import cxBaseC
#from cxBase.Conf import cxConfC
from IndriRelate.IndriPackedRes import *
from IndriRelate.IndriInferencer import *
from IndriRelate.CtfLoader import TermCtfC
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
        self.Lambda = 0.15
        self.NumOfSt = 20
        self.DocProbNamePre = ""
        self.OutName = ""
        self.TopicTermIn = ""
        self.hQTopicTerm = {} #qid->[term,weight]
        self.Inferencer = LmInferencerC()
        self.CtfCenter = TermCtfC()
        
        
    @staticmethod
    def ShowConf():
        cxBaseC.ShowConf()
        print "datadir\nin\nout\ncachedir\ntopdocn\nlambda\ndocprobpre\nlambda\ntopicterm(ifneed)\nctf"
        
    def SetConf(self, ConfIn):
        cxBaseC.SetConf(self, ConfIn)
        self.DataDir = self.conf.GetConf('datadir') + '/'
        self.QIn = self.conf.GetConf('in')
        self.OutName = self.conf.GetConf('out')
        self.CacheDir = self.conf.GetConf('cachedir') + '/'
        self.TopDocN = int(self.conf.GetConf('topdocn'))
        self.Lambda = float(self.conf.GetConf('lambda', self.Lambda))
        self.DocProbNamePre = self.conf.GetConf('docprobpre')
        self.TopicTermIn = self.conf.GetConf('topictermin')
        self.NumOfSt = int(self.conf.GetConf('numofst', self.NumOfSt))
        if "" != self.TopicTermIn:
            self.ReadTopicTerm()
        self.CtfCenter = TermCtfC(self.conf.GetConf('ctf'))
        
    
    def ReadTopicTerm(self):
        for line in open(self.TopicTermIn):
            qid,query,term,score = line.strip().split('\t')
            if not qid in self.hQTopicTerm:
                self.hQTopicTerm[qid] = []
            if len(self.hQTopicTerm[qid]) < self.NumOfSt:
                self.hQTopicTerm[qid].append([term,score])
    
    def GetDocProb(self,qid,query,lDoc):
        if {} == self.hQTopicTerm:
            lDocNo =[doc.DocNo for doc in lDoc]
            lDocProbVec = self.ReadDocProbVec(lDocNo, qid)
            return lDocProbVec
        
        lTopicTerm = self.hQTopicTerm[qid]
        lDocProbVec = []
        for doc in lDoc:
            lTopicWeight = []
            Lm = LmBaseC(doc)
            for term,weight in lTopicTerm:
                prob = self.Inferencer.InferQuery(query + " " + term, Lm, self.CtfCenter)
                lTopicWeight.append(prob)
            Vector = VectorC(lTopicWeight)
            lDocProbVec.append(Vector)
        return lDocProbVec
        
    
    
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
        lDocProbVec = self.GetDocProb(qid,query,lDoc)        
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
        