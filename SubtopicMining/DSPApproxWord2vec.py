'''
Created on my MAC Nov 16, 2014-8:46:48 PM
What I do:
I am the word2vec version of DSPApprox
besides the p(t|v) for predictiveness
Also use word2vec
Average distance with uncovered vocabulary
What's my input:
DSPApprox (and word2vec can be loaded from the dir)
What's my output:
same as DSPApproxC
@author: chenyanxiong
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
from cxBase.Vector import VectorC
from DSPApprox import DSPApproxC


class DSPApproxWord2VecC(DSPApproxC):
    
    def Init(self):
        DSPApproxC.Init(self)
        self.CenterWeight = 1.0
        
        
    def LoadWord2Vec(self,qid,hVocabulary):
        lWord2Vec = []
        lLine = open(self.WordDataDir + '/%s_word2vec' %(qid)).read().splitlines()
        lWord2VecTerm = open(self.WordDataDir + '/%s_word2vec_term' %(qid)).read().splitlines()
        hWord2VecTerm = dict(zip(lWord2VecTerm,range(len(lWord2VecTerm))))
        for term in hVocabulary.keys():
            Vector = VectorC()
            if term in hWord2VecTerm:
                line = lLine[hWord2VecTerm[term]]
                print "converting line [%s] for term [%s]" %(line,term)
                lDim = [float(item) for item in line.split(',')]
                Vector=VectorC(lDim)
            lWord2Vec.append(Vector)
        return lWord2Vec
    
    def CalcCenterality(self,hTopicTerm,hVocabulary,lWord2Vec):
        hTermCenterality = {} #term -> 1/Z \sum distance with vocabulary
        Z = float(len(hVocabulary))
        for term in hTopicTerm.keys():
            Vector = lWord2Vec[hVocabulary[term]]
            centerality = 0
            for Vb in lWord2Vec:
                centerality += VectorC.cosine(Vector, Vb) /Z
            hTermCenterality[term] = centerality
        print "centerality calculated"
        return
    
    def UpdateCenterality(self,hPreProb,lCoveredTerm,hTermCenterality,lWord2Vec,hVocabulary):
        lNewCover = [term for term in hPreProb.keys() if not term in lCoveredTerm]
        Z = float(len(hVocabulary))
        for term,centerality in hTermCenterality.items():
            for CoveredTerm in lNewCover:
                Va = lWord2Vec[hVocabulary[term]]
                Vb = lWord2Vec[hVocabulary[CoveredTerm]]
                centerality -= VectorC.cosine(Va,Vb) / Z
            hTermCenterality[term] = centerality
        return hTermCenterality
    
    def ProcessOneQ(self,qid,query):
        '''
        read and make topic terms
        read and make predictiveness
        select terms greedly
            pick current best
            update predictiveness and covered terms
        '''
        print 'start working on [%s][%s]' %(qid,query)
        lTopicTermWeight = []  #(term,weight)
        lCoveredTerm = []
        
        lDoc = ReadPackedIndriRes(self.CacheDir + '/' + query, self.TopDocN)
        hTopicTerm = self.GenerateTopicTerms(qid,query, lDoc)
        print "candidate topic terms num [%d]" %(len(hTopicTerm))
        hTopicTermPreProb,hPredictiveness,hVocabulary = self.LoadOccurMatrix(qid, query, hTopicTerm)
        lWord2Vec = self.LoadWord2Vec(qid, hVocabulary)
        hTermCenterality = self.CalcCenterality(hTopicTerm, hVocabulary, lWord2Vec)
        
        while hTopicTerm != {}:
            BestTerm,score = self.CalcCurrentBest(hTopicTerm, hPredictiveness,hTermCenterality)
            lTopicTermWeight.append([BestTerm,score])
            del hTopicTerm[BestTerm]
            hPreProb = hTopicTermPreProb[BestTerm]
            hPredictiveness = self.UpdatePredictiveness(hPreProb, lCoveredTerm, hPredictiveness, hTopicTermPreProb,hVocabulary)
            hTermCenterality = self.UpdateCenterality(hPreProb, lCoveredTerm, hTermCenterality, lWord2Vec, hVocabulary)
            lCoveredTerm = self.UpdateCovedTerm(hPreProb, lCoveredTerm)
            print "current best [%s][%f]" %(BestTerm,score)
        
        return lTopicTermWeight
    
        
    
    def CalcCurrentBest(self,hTopicTerm,hPredictiveness,hTermCenterality):
        BestTerm = ""
        score = 0
        
        for term,topicality in hTopicTerm.items():
            pred = hPredictiveness[term]
            centerality = hTermCenterality[term]
            ThisScore = topicality * pred * math.pow(centerality,self.CenterWeight)
            if ThisScore > score:
                score = ThisScore
                BestTerm = term
        
        return BestTerm,score
                
                
                
        
            
        
        
        
        

