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
from IndriRelate.IndriPackedRes import ReadPackedIndriRes
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
        
        
    @staticmethod
    def ShowConf():
        cxBaseC.ShowConf()
        print "cachedir\nin\nout\ntopdocn\nuwsize\n"
        
    def SetConf(self, ConfIn):
        cxBaseC.SetConf(self, ConfIn)
        self.UWSize = int(self.conf.GetConf('uwsize', self.UWSize))
        self.TopDocN = int(self.conf.GetConf('topdocn', self.TopDocN))
        self.CacheDir = self.conf.GetConf('cachedir') + '/'
        self.QIn = self.conf.GetConf('in')
        self.OutDir = self.conf.GetConf('out')
        
        
        
        
        
    def GenerateForOneQ(self,query):
        lDoc = ReadPackedIndriRes(self.CacheDir + query,self.TopDocN)
        
        hTermCooccur = {}  #term id\tterm id -> cnt   id 1 < id 2
        lTerm = []    #the hash list of terms
        
        
        for doc in lDoc:
            lTermPair = self.GenerateTermPairForDoc(doc)
            hTermCooccur,lTerm = self.UpdateDataWithTriples(lTermPair,hTermCooccur,lTerm)
            
        return hTermCooccur,lTerm
    
    
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
            
        return lPair
    
    def UpdataDataWithTriples(self,lTermPair,hTermCooccur,lTerm):
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
        return hTermCooccur,lTerm
    
    def ProcessOneQ(self,qid,query):
        hTermCooccur,lTerm = self.GenerateForOneQ(query)
        
        TermIdOut = open(self.OutDir + '/%s_term' %(qid))
        print >> TermIdOut, '\n'.join(lTerm)
        TermIdOut.close()
        OccurOut = open(self.OutDir + '%s_occur' %(qid))
        for key,value in hTermCooccur.items():
            print >> OccurOut,key + ',%d' %(value)
        OccurOut.close()
        
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
                    

