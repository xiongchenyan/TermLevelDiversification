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
        self.NumOfSt = len(lDocProbVec[0].hDim)
        lUnsatisfy = [1.0 / self.NumOfSt] * self.NumOfSt
        
        while len(lRerankDocNo) < len(lDoc):
            NextP,score = self.SelectNextBest(lDoc,lDocProbVec,lUnsatisfy,lRerankDocNo)
            lRerankDocNo.append(lDoc[NextP].DocNo)
            lDocScore.append(score)
            lUnsatisfy = self.UpdateUnsatisfy(lDocProbVec[NextP],lUnsatisfy)
        
        return lRerankDocNo
    
    
    def SelectNextBest(self,lDoc,lDocProbVec,lUnsatisfy,lRerankDocNo):
        MaxScore = -1
        NextP = 0
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
