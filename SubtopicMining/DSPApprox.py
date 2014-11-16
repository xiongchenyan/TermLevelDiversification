'''
Created on Nov 16, 2014 3:00:53 PM
@author: cx

what I do:
I generate topic terms using DSP approx
what's my input:
query, cachedir, and the data dir prepared by WordDataPreparation
what's my output:
topic terms for each query, as the output of DSPApprox
'''


import site
site.addsitedir('/bos/usr0/cx/PyCode/cxPyLib')
site.addsitedir('/bos/usr0/cx/PyCode/GoogleAPI')

import math
import sys
from cxBase.base import cxBaseC
from cxBase.Conf import cxConfC
from IndriRelate.IndriPackedRes import *
from IndriRelate.IndriInferencer import *
from IndriRelate.CtfLoader import TermCtfC
class DSPApproxC(cxBaseC):
    def Init(self):
        self.UWSize = 20
        self.TopDocN = 100
        self.CacheDir = ""
        self.CtfCenter = TermCtfC()
        self.WordDataDir = ""
        self.QIn = ""
        self.TopicTermOut = ""
        
    def SetConf(self, ConfIn):
        cxBaseC.SetConf(self, ConfIn)
        self.UWSize = int(self.conf.GetConf('uwsize', self.UWSize))
        self.TopDocN = int(self.conf.GetConf('topdocn', self.TopDocN))
        self.CacheDir = self.conf.GetConf('cachedir')
        self.CtfCenter.load(self.conf.GetConf('ctf'))
        self.WordDataDir = self.conf.GetConf('worddatadir') + '/'
        self.QIn = self.conf.GetConf('in')
        self.TopicTermOut = self.conf.GetConf('out')
        
        
    @staticmethod
    def ShowConf():
        cxBaseC.ShowConf()
        print 'uwsize\ntopdocn\ncachedir\nctf\nworddatadir\nin\nout'
        
        
    
    def GenerateTopTerms(self,query,lDoc):
        #query need to be stemmed
        hTopicTerm = {}   #term -> topicality
        
        
        lQTerm = query.split()
        
        for doc in lDoc:
            lDocTerm = doc.GetContent().split()
            lQIndicex = [i for i,term in enumerate(lDocTerm) if term in lQTerm]
            for indice in lQIndicex:
                lTerm = lDocTerm[max(0,indice-self.UWSize):indice + self.UWSize]
                hTopicTerm.update(dict(zip(lTerm,[0]*len(lTerm))))
                
        #calc topicality
        for doc in lDoc:
            Lm = LmBaseC(doc)
            for term in hTopicTerm.keys():
                hTopicTerm[term] += Lm.GetTFProb(term) * math.exp(doc.score)
                
        
        #replace with KL
        for term,value in hTopicTerm.items():
            ctf = self.CtfCenter.GetCtfProb(term)
            hTopicTerm[term] = value * math.log(value / ctf)
        
        return hTopicTerm
    
    
    def LoadOccurMatrix(self,qid,query,hTopicTerm):
        hTopicTermPreProb = {}   #topic term -> hPred[term]->p(t|v)
        #all read from disk
        
        '''
        load the lVovabulary, and the sparse format matrices in disk
            (transfer sparse format matrices in lhDict format)
            (normalize by column) (row indices use term, column just ids)
        for each topic term, sum it up (normalized with vocabulary size)
        '''
        TermInName = self.WordDataDir + '%d_term' %(qid)
        CoocInName = self.WordDataDir + '%d_occur' %(qid)
        
        lVocabulary = open(TermInName).read().split('\n')
        lColSum = [0] * len(lVocabulary)
        for line in open(TermInName):
            p,q,value = line.strip().split(',')
            p = int(p)
            q = int(q)
            value = int(value)
            term = lVocabulary[p-1]
            lVocabulary[q-1] += value
            if not term in hTopicTermPreProb:
                hPred = {q:value}
                hTopicTermPreProb[term] = hPred
            else:
                if not q in hTopicTermPreProb[term]:
                    hTopicTermPreProb[term][q] = value
                else:
                    hTopicTermPreProb[term][q] += value
                    
        for term in hTopicTermPreProb.keys():
            for q in hTopicTermPreProb[term].keys():
                hTopicTermPreProb[term][q] /= float(lColSum[q - 1])
        return hTopicTermPreProb,lVocabulary
    
    
    def ProcessOneQ(self,qid,query):
        lTopicTermWeight = []  #(term,weight)
        lVocabularty = []
        hTopicTerm = {}
        hPredictiveness = {}
        hTopicTermPreProb = {}
        lCoveredTerm = []
        
        
        
        return lTopicTermWeight
        
    
    def CalcCurrentBest(self,hTopicTerm,hPredictiveness):
        BestTerm = ""
        score = 0
        
        for term,topicality in hTopicTerm:
            pred = hPredictiveness[term]
            if topicality * pred > score:
                score = topicality * pred
                BestTerm = term
        
        return BestTerm,score
    
    def UpdatePredictiveness(self,hPreProb,lCoveredTerm,hPredictiveness,hTopicTermPreProb):
        
        
        return hPredictiveness
    
    def UpdateCovedTerm(self,hPreProb,lCoveredTerm):
        
        return lCoveredTerm
    
        
    def Process(self):
        
        
        
        return
        
        


