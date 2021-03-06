'''
Created on Nov 9, 2014 2:19:03 PM
@author: cx

what I do:
I re rank documents using xQuAd algorithm
what's my input:
I am a sub class of DiversifiedRerankC
lDoc, lDocProbVector
what's my output:
reranked DocNo
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
from Reranking.DiversifiedRerank import DiversifiedRerankC
import math

class xQuAdRerankerC(DiversifiedRerankC):
    
    def RerankForOneQ(self, qid, query, lDoc, lDocProbVec):
        lRerankDocNo = []
        lDocScore = []
        if [] == lDocProbVec:
            lRerankDocNo = [doc.DocNo for doc in lDoc]
            lDocScore = [doc.score for doc in lDoc]
            return lRerankDocNo,lDocScore
        
#         self.NumOfSt = min(len(lDocProbVec[0].hDim),self.NumOfSt)
        NumOfSt = len(lDocProbVec[0].hDim)
        print '[%s][%s] have [%d] st' %(qid,query,NumOfSt)
        lUnsatisfy = [1.0 / self.NumOfSt] * self.NumOfSt
        
        while len(lRerankDocNo) < len(lDoc):
            NextP,score = self.SelectNextBest(lDoc,lDocProbVec,lUnsatisfy,lRerankDocNo)
            if -1 == NextP:
                print "select next best failed"
                break
            lRerankDocNo.append(lDoc[NextP].DocNo)
            lDocScore.append(score)
            lUnsatisfy = self.UpdateUnsatisfy(lDocProbVec[NextP],lUnsatisfy)
        
        return lRerankDocNo,lDocScore
    
    
    def SelectNextBest(self,lDoc,lDocProbVec,lUnsatisfy,lRerankDocNo):
        MaxScore = -10000000
        NextP = -1
        for i in range(len(lDoc)):
            if lDoc[i].DocNo in lRerankDocNo:
                continue
            ThisDocScore = self.CalcDocScore(lDoc[i],lDocProbVec[i],lUnsatisfy)
            if ThisDocScore> MaxScore:
                MaxScore = ThisDocScore
                NextP = i
        return NextP,MaxScore
    
    def CalcDocScore(self,doc,DocProbVec,lUnsatisfy):
        res = (1-self.Lambda) * math.exp(doc.score)
        for key,value in DocProbVec.hDim.items():
            key = int(key)
            res += self.Lambda * lUnsatisfy[key] * value
        return res
        
    def UpdateUnsatisfy(self,DocProbVec,lUnsatisfy):
        for i in range(len(lUnsatisfy)):
            score = DocProbVec.GetDim(str(i))
            lUnsatisfy[i] *= 1 - score
        return lUnsatisfy
