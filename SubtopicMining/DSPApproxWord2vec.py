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
        for i in range(len(hVocabulary)):
            lWord2Vec.append(VectorC()) 
        lLine = open(self.WordDataDir + '/%s_word2vec' %(qid)).read().splitlines()
        lWord2VecTerm = open(self.WordDataDir + '/%s_word2vec_term' %(qid)).read().splitlines()
        hWord2VecTerm = dict(zip(lWord2VecTerm,range(len(lWord2VecTerm))))
        for term,p in hVocabulary.items():
            if term in hWord2VecTerm:
                line = lLine[hWord2VecTerm[term]]
#                 print "converting line [%s] for term [%s]" %(line,term)
                lDim = [float(item) for item in line.split(',')]
                lWord2Vec[p] = VectorC(lDim)
        return lWord2Vec
    
    def CalcCenterality(self,hTopicTerm,hVocabulary,lWord2Vec):
        hTermCenterality = {} #term -> 1/Z \sum distance with vocabulary
        hTermL2Dis = {}   #term ->[L2 dis with all vocabulary]
        Z = float(len(hVocabulary))
        lVocabulary = hVocabulary.items()
        lVocabulary.sort(key=lambda item:int(item[1]))
        lVocabulary =[item[0] for item in lVocabulary]
        for term in hTopicTerm.keys():
            Vector = lWord2Vec[hVocabulary[term]]
            hTermL2Dis[term] = []
            centerality = 0
            for i in range(len(lWord2Vec)):
                if i == hVocabulary[term]:
                    hTermL2Dis[term].append(0)
                    continue
                Vb = lWord2Vec[i]
                if Vb.hDim == {}:
                    hTermL2Dis[term].append(0)
                    continue
                L2Dis = VectorC.L2Distance(Vector, Vb)
#                 print "L2[%s]-[%s]: [%f]" %(term,lVocabulary[i],L2Dis)
#                 print json.dumps(Vector.hDim)
#                 print json.dumps(Vb.hDim)
                hTermL2Dis[term].append(L2Dis)
                if 0 == L2Dis:
                    continue
                centerality +=  1.0/(Z * L2Dis)
            hTermCenterality[term] = centerality
            print "term [%s] centerality [%f]" %(term,centerality)
        print "centerality calculated"
        return hTermCenterality,hTermL2Dis
    
    def UpdateCenterality(self,hPreProb,lCoveredTerm,hTermCenterality,hTermL2Dis,lWord2Vec,hVocabulary):
        lNewCover = [term for term in hPreProb.keys() if not term in lCoveredTerm]
#         print "newly covered term p[%s]" %(json.dumps(lNewCover))
        Z = float(len(hVocabulary))
        for term,centerality in hTermCenterality.items():
            for CoveredTermP in lNewCover:
                L2Dis = hTermL2Dis[term][CoveredTermP]
                if 0 == L2Dis:
                    continue
                centerality -= 1.0/(L2Dis* Z)
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
        hTermCenterality,hTermL2Dis = self.CalcCenterality(hTopicTerm, hVocabulary, lWord2Vec)
        
        while hTopicTerm != {}:
            BestTerm,score = self.CalcCurrentBest(hTopicTerm, hPredictiveness,hTermCenterality)
            if "" == BestTerm:
                print "no more positive topic term found, break"
                break
            lTopicTermWeight.append([BestTerm,score])
            del hTopicTerm[BestTerm]
            hPreProb = hTopicTermPreProb[BestTerm]
            hPredictiveness = self.UpdatePredictiveness(hPreProb, lCoveredTerm, hPredictiveness, hTopicTermPreProb,hVocabulary)
            hTermCenterality = self.UpdateCenterality(hPreProb, lCoveredTerm, hTermCenterality, hTermL2Dis,lWord2Vec, hVocabulary)
            lCoveredTerm = self.UpdateCovedTerm(hPreProb, lCoveredTerm)
            print "current best [%s][%f]" %(BestTerm,math.log(score))
        
        return lTopicTermWeight
    
        
    
    def CalcCurrentBest(self,hTopicTerm,hPredictiveness,hTermCenterality):
        BestTerm = ""
        score = 0
        
        for term,topicality in hTopicTerm.items():
            pred = hPredictiveness[term]
            centerality = hTermCenterality[term]
            if (pred < 0) | (topicality < 0):
                continue
            WeightedCenterality = math.pow(centerality,self.CenterWeight)
            ThisScore = topicality * pred *  WeightedCenterality
            if ThisScore > score:
                score = ThisScore
                BestTerm = term
                print "get better term [%s][%f,%f,%f][%f]" %(term,topicality,pred,WeightedCenterality,ThisScore)
        
        return BestTerm,score
                
                
                
        
            
        
        
        
        

