'''
Created on Oct 19, 2014 3:09:03 PM
@author: cx

what I do:
generate the word-word cnt matrix for each query
from top n doc (n=100)
uw size is 20
what's my input:
query, Indri Cache dir
what's my output:
for each query, two files:
    1: word,word,co occurance cnt
    2: word hash id (start from 1)
'''

import site
site.addsitedir('/bos/usr0/cx/PyCode/cxPyLib')
import os
from cxBase.base import cxBaseC
#from cxBase.Conf import cxConfC
from IndriRelate.IndriPackedRes import *
from cxBase.TextBase import TextBaseC

class WordCooccurGeneratorC(cxBaseC):
    
    def Init(self):
        cxBaseC.Init(self)
        self.UWSize = 20
        self.TopDocN = 100
        self.CacheDir = ""
        self.QIn = ""
        self.OutDir = ""
        self.MinPairCnt = 10
        self.MinTF = 100
        
    @staticmethod
    def ShowConf():
        cxBaseC.ShowConf()
        print "cachedir\nin\noutdir\ntopdocn\nuwsize\n"
        
    def SetConf(self, ConfIn):
        cxBaseC.SetConf(self, ConfIn)
        self.UWSize = int(self.conf.GetConf('uwsize', self.UWSize))
        self.TopDocN = int(self.conf.GetConf('topdocn', self.TopDocN))
        self.CacheDir = self.conf.GetConf('cachedir') + '/'
        self.QIn = self.conf.GetConf('in')
        self.OutDir = self.conf.GetConf('outdir') + '/'
        
        
        
        
        
    def GenerateForOneQ(self,query):
        lDoc = ReadPackedIndriRes(self.CacheDir + query,self.TopDocN)
        
        hTermCooccur = {}  #term id\tterm id -> cnt   id 1 < id 2
        lTerm = []    #the hash list of terms
        
        
        for doc in lDoc:
            lTermPair = self.GenerateTermPairForDoc(doc)
            hTermCooccur,lTerm = self.UpdateDataWithPairs(lTermPair,hTermCooccur,lTerm)
            del lTermPair[:]
        hTermCooccur,lTerm = self.TermPairFilter(hTermCooccur, lTerm)
        return hTermCooccur,lTerm
    
    
    def TermPairFilter(self,hTermCooccur,lTerm):
        '''
        filter term pairs and terms to speed up
        discard term that tf < 100
        discard term pair that cnt < 10
        '''
        hNewCooc = self.DiscardTermPairByCnt(hTermCooccur)
        hNewCooc,lNewTerm = self.DiscardTermByTF(hNewCooc, lTerm)
        
        print "after filters [%d]-> [%d] term, [%d]->[%d] pair" %(len(lTerm),len(lNewTerm),len(hTermCooccur),len(hNewCooc))
        return hNewCooc,lNewTerm
    
    
    def DiscardTermPairByCnt(self,hTermCooccur):
        hNewTermCooc = {}
        for key,value in hTermCooccur.items():
            if value >= self.MinPairCnt:
                hNewTermCooc[key] = value
        return hNewTermCooc
    
    def DiscardTermByTF(self,hTermCooccur,lTerm):
        lTermCnt = [0] * len(lTerm)
        for key,value in hTermCooccur.items():
            pa,pb = key.split(',')
            pa = int(pa) - 1
            pb = int(pb) - 1
            lTermCnt[pa] += value
            lTermCnt[pb] += value
        
        l = sorted(lTermCnt,reverse = True)
        self.MinTF = max(self.MinTF,l[1000])
            
        hTermStrCooc = {}
        lNewTerm = []
        
        #put term pairs that should be kept in h and l
        for i in range(len(lTerm)):
            if lTermCnt[i] < self.MinTF:
                continue
            lNewTerm.append(lTerm[i])
        for key,value in hTermCooccur.items():
            pa,pb = key.split(',')
            pa = int(pa) - 1
            pb = int(pb) - 1
            ta = lTerm[pa]
            tb = lTerm[pb]
            if (ta in lNewTerm) & (tb in lNewTerm):
                NewPa = lNewTerm.index(ta) + 1
                NewPb = lNewTerm.index(tb)  + 1
                NewKey = str(NewPa) + ',' + str(NewPb)
                hTermStrCooc[NewKey] = value
        return hTermStrCooc,lNewTerm
    
    
    def GenerateTermPairForDoc(self,doc):
        
        text = doc.GetContent()
        text = TextBaseC.RawClean(text)
        lTermSeq = text.split(' ')
        
        SlidingSize = self.UWSize / 2
        
        lCurrentTerm = []
        lPair = []
        
        for term in lTermSeq:
            if [] != lCurrentTerm:
                for PreTerm in lCurrentTerm:
                    lPair.append([PreTerm,term])
            lCurrentTerm.append(term)
            if len(lCurrentTerm) > SlidingSize:
                del lCurrentTerm[0]
        print "Get [%d] term pairs from doc [%s]" %(len(lPair),doc.DocNo)    
        return lPair
    
    def UpdateDataWithPairs(self,lTermPair,hTermCooccur,lTerm):
        '''
        update the hash ids and the term cooccur cnt
        '''
        
        for Ta,Tb in lTermPair:        
            #get hash id
            if not Ta in lTerm:
                lTerm.append(Ta)
            if not Tb in lTerm:
                lTerm.append(Tb)
            
            pa = lTerm.index(Ta) + 1
            pb = lTerm.index(Tb) + 1
            
            if pa > pb:
                pa,pb = pb,pa
            
            Key = str(pa) + ',' + str(pb)
            if not Key in hTermCooccur:
                hTermCooccur[Key] = 1
            else:
                hTermCooccur[Key] += 1
        print 'current term num [%d] pair [%d]' %(len(lTerm),len(hTermCooccur))
        return hTermCooccur,lTerm
    
    def ProcessOneQ(self,qid,query):
        print "start processing [%s][%s]" %(qid,query)
        hTermCooccur,lTerm = self.GenerateForOneQ(query)
        
        TermIdOut = open(self.OutDir + '/%s_term' %(qid),'w')
        print >> TermIdOut, '\n'.join(lTerm)
        print "get [%d] terms from SERP" %(len(lTerm))
        TermIdOut.close()
        OccurOut = open(self.OutDir + '%s_occur' %(qid),'w')
        for key,value in hTermCooccur.items():
            print >> OccurOut,key + ',%d' %(value)
        OccurOut.close()

        del hTermCooccur
        del lTerm[:]
        return
    
    
    def Process(self):
        if not os.path.exists(self.OutDir):
            os.makedirs(self.OutDir)
            
        for line in open(self.QIn):
            qid,query = line.strip().split('\t')            
            self.ProcessOneQ(qid, query)
            print "[%s] processed" %(line.strip())
        return
    
    
    

import sys

if 2 !=len(sys.argv):
    WordCooccurGeneratorC.ShowConf()
    sys.exit()
    

Processor = WordCooccurGeneratorC(sys.argv[1])
Processor.Process()
print "finished"     
                    

