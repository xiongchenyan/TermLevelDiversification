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
        self.DataSuf = ""
        
    def SetConf(self, ConfIn):
        cxBaseC.SetConf(self, ConfIn)
        self.UWSize = int(self.conf.GetConf('uwsize', self.UWSize))
        self.TopDocN = int(self.conf.GetConf('topdocn', self.TopDocN))
        self.CacheDir = self.conf.GetConf('cachedir')
        self.CtfCenter.Load(self.conf.GetConf('ctf'))
        self.WordDataDir = self.conf.GetConf('worddatadir') + '/'
        self.QIn = self.conf.GetConf('in')
        self.TopicTermOut = self.conf.GetConf('out')
        
        
    @staticmethod
    def ShowConf():
        cxBaseC.ShowConf()
        print 'uwsize\ntopdocn\ncachedir\nctf\nworddatadir\nin\nout'
        
        
    
    def GenerateTopicTerms(self,qid,query,lDoc):
        #query need to be stemmed
        hTopicTerm = {}   #term -> topicality
        lTermSet = open(self.WordDataDir + '%s_term' %(qid)).read().split('\n')
        
        lQTerm = query.split()
        
        for doc in lDoc:
            lDocTerm = doc.GetContent().lower().split()
            lQIndicex = [i for i,term in enumerate(lDocTerm) if term in lQTerm]
            for indice in lQIndicex:
                lTerm = lDocTerm[max(0,indice-self.UWSize):indice + self.UWSize]
                lTargetTerm = [term for term in lTerm if (term in lTermSet) & (not term in lQTerm)]
                hTopicTerm.update(dict(zip(lTargetTerm,[0]*len(lTargetTerm))))
                
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
        hPredictiveness = {}   #term->sum of hPred[term]
        #all read from disk
        
        '''
        load the lVovabulary, and the sparse format matrices in disk
            (transfer sparse format matrices in lhDict format)
            (normalize by column) (row indices use term, column just ids)
        for each topic term, sum it up (normalized with vocabulary size)
        '''
        TermInName = self.WordDataDir + '%s%s_term' %(qid,self.DataSuf)
        CoocInName = self.WordDataDir + '%s%s_occur' %(qid,self.DataSuf)
        
        lVocabulary = open(TermInName).read().split('\n')
        lColSum = [0] * len(lVocabulary)
        for line in open(CoocInName):
            p,q,value = line.strip().split(',')
            p = int(p)
            q = int(q)
            value = int(value)
            term = lVocabulary[p-1]
            lColSum[q-1] += value
            if not term in hTopicTermPreProb:
                hPred = {q:value}
                hTopicTermPreProb[term] = hPred
            else:
                if not q in hTopicTermPreProb[term]:
                    hTopicTermPreProb[term][q] = value
                else:
                    hTopicTermPreProb[term][q] += value
        
        hPredictiveness = dict(zip(hTopicTermPreProb.keys(),[0]*len(hTopicTermPreProb)))
                    
        for term in hTopicTermPreProb.keys():
            for q in hTopicTermPreProb[term].keys():
                hTopicTermPreProb[term][q] /= float(lColSum[q - 1])
                hPredictiveness[term] += hTopicTermPreProb[term][q] / float(len(lVocabulary))
        
        hVocabulary = dict(zip(lVocabulary,range(len(lVocabulary))))        
        return hTopicTermPreProb,hPredictiveness,hVocabulary
    
    
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
        print "read [%d] docs" %(len(lDoc))
        hTopicTerm = self.GenerateTopicTerms(qid,query, lDoc)
        print "candidate topic terms num [%d]" %(len(hTopicTerm))
        hTopicTermPreProb,hPredictiveness,hVocabularty = self.LoadOccurMatrix(qid, query, hTopicTerm)
        
        while hTopicTerm != {}:
            BestTerm,score = self.CalcCurrentBest(hTopicTerm, hPredictiveness)
            lTopicTermWeight.append([BestTerm,score])
            del hTopicTerm[BestTerm]
            hPreProb = hTopicTermPreProb[BestTerm]
            hPredictiveness = self.UpdatePredictiveness(hPreProb, lCoveredTerm, hPredictiveness, hTopicTermPreProb,hVocabularty)
            lCoveredTerm = self.UpdateCovedTerm(hPreProb, lCoveredTerm)
            print "current best term [%s][%f]" %(BestTerm,score)
        
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
    
    def UpdatePredictiveness(self,hPreProb,lCoveredTerm,hPredictiveness,hTopicTermPreProb,hVocabulary):
        '''
        get newly covered terms (in hPreProb, not in lCoveredTerm)
        for each term in hPredictiveness, minus \sum p(term|v) for all v in newly covered terms
        '''
        
        lNewCover = [key for key in hPreProb.keys() if not key in lCoveredTerm]
        Z = float(len(hVocabulary))
        for term,Predict in hPredictiveness.items():
            hThisTermPre = hTopicTermPreProb[term]
            for CoverTerm in lNewCover:
                if CoverTerm in hThisTermPre:
                    Predict -= hThisTermPre[CoverTerm] / Z
            hPredictiveness[term] = Predict
        
        return hPredictiveness
    
    def UpdateCovedTerm(self,hPreProb,lCoveredTerm):
        for term in hPreProb.keys():
            if not term in lCoveredTerm:
                    lCoveredTerm.append(term)
        return lCoveredTerm
    
        
    def Process(self):
        out = open(self.TopicTermOut,'w')
        for line in open(self.QIn):
            qid,query = line.strip().split('\t')
            lTopicTermWeight = self.ProcessOneQ(qid, query)
            for term,score in lTopicTermWeight:
                print >>out, qid + '\t' + query +'\t%s\t%f' %(term,score)
            print '[%s] finished' %(query)
        out.close()
            
        print "finished"
        return
        
        
# import sys
# 
# if 2 != len(sys.argv):
#     DSPApproxC.ShowConf()
#     sys.exit()
#     
# Processor = DSPApproxC(sys.argv[1])
# Processor.Process()


