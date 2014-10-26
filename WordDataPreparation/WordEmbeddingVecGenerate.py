'''
Created on Oct 19, 2014 3:55:16 PM
@author: cx

what I do:
for each query's terms (as the output of WordCooccurGenerate)
    fetch its word embedding, and output to a new matrix file
what's my input:
the output dir of WordCoocurGenerator()
what's my output:
for each query:
    qid_word2vec:
        each line is the word2vec of a term in qid_term
'''


import site
site.addsitedir('/bos/usr0/cx/PyCode/cxPyLib')
site.addsitedir('/bos/usr0/cx/PyCode/GoogleAPI')
from word2vec.WordVecBase import Word2VecC,Word2VecReaderC
from word2vec.WordVecBatchFetcher import WordVecBatchFetcher
import os

from cxBase.Conf import cxConfC
from cxBase.base import cxBaseC


class WordEmbeddingVecGeneratorC(cxBaseC):
    def Init(self):
        cxBaseC.Init(self)
        self.Word2vecIn = ""
        self.DataDir = ""
        
    @staticmethod
    def ShowConf():
        cxBaseC.ShowConf()
        print "word2vecin\ndatadir"
        
    
    def SetConf(self, ConfIn):
        cxBaseC.SetConf(self, ConfIn)
        self.Word2vecIn = self.conf.GetConf('word2vecin')
        self.DataDir = self.conf.GetConf('datadir') + '/'
        
        
        
    def ReadAllTerm(self):
        #cause I need batch fetch word2vec
        hTerm = {}
        for qid in range(1,201):
            InName = self.DataDir + '/%d_term' %(qid)
            for line in open(InName):
                hTerm[line.strip()] = ""
                
                
        return hTerm.key()
    
    
    def DumpMtxForOneQ(self,qid,lTerm,lWord2Vec):
        InName = self.DataDir + '%d_term' %(qid)
        OutName = self.DataDir + '%d_word2vec' %(qid)
        
        out = open(OutName,'w')
        OutInTerm = open(OutName + '_term','w')
        cnt = 0
        InCnt = 0
        for line in open(InName):
            cnt += 1
            term = line.strip()
            p = lTerm.Index(term)
            Vector = lWord2Vec[p]
            Mids = Vector.dumps()
            EmbeddingStr = Mids.split('\t')[1].replace(' ',',')
            if not Vector.IsEmpty():           
                print >>out,EmbeddingStr
                print >>OutInTerm,term
                InCnt += 1
        
        out.close()
        OutInTerm.close()
        print '[%d] query finished [%d]/[%d] in' %(qid,InCnt,cnt)
        return
    
    def Process(self):
        print "start to read terms"
        lAllTerm = self.ReadAllTerm()
        print 'get total [%d] terms' %(len(lAllTerm))
        lWord2Vec = WordVecBatchFetcher(lAllTerm, self.Word2vecIn)
        
        for qid in range(1,201):
            self.DumpMtxForOneQ(qid, lAllTerm, lWord2Vec)
            
        print "all word2vec fetched"
        
        
import sys

if 2 != len(sys.argv):
    WordEmbeddingVecGeneratorC.ShowConf()
    sys.exit()
    
Generator = WordEmbeddingVecGeneratorC(sys.argv[1])
Generator.Process()
        
        
        
        
        
        
        
        
