'''
Created on Nov 9, 2014 4:36:13 PM
@author: cx

what I do:
I re rank using PM2 algorithm
what's my input:
lDoc, lDocProbVec
what's my output:
lRerankDocNo, lDocScore

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

class PM2RerankerC(DiversifiedRerankC):
    
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
        self.NowNeedSt = lUnsatisfy.index(max(lUnsatisfy))
        
        NextP = 0
        for i in range(len(lDoc)):
            if lDoc[i].DocNo in lRerankDocNo:
                continue
            ThisDocScore = self.CalcScore(lDoc[i],lDocProbVec[i],lUnsatisfy)
            if (ThisDocScore > MaxScore) | (MaxScore == -1):
                MaxScore = ThisDocScore
                NextP = i
        return NextP,MaxScore
                
                
    def CalcScore(self,doc,DocProbVec,lUnsatisfy):
        res = 0
        for key,value in DocProbVec.hDim.items():
            key = int(key)
            mid = self.Lambda
            if self.NowNeedSt != key:
                mid = 1 - self.Lambda
            res += mid * lUnsatisfy[key] * value
        return res
    
    def UpdateUnsatisfy(self,DocProbVec,lUnsatisfy):
        if [] == lUnsatisfy:
            return
        SumTopProb = sum(DocProbVec.hDim.values())
        w = 1.0 / len(lUnsatisfy)
        
        
        for key,value in DocProbVec.hDim.items():
            key = int(key)
            si = ((w / lUnsatisfy[key]) - 1.0) / 2.0
            si += value / SumTopProb
            lUnsatisfy[key] = w / (2*si + 1.0)
        return 
                
        
