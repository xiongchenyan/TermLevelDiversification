'''
Created on Oct 19, 2014 4:35:44 PM
@author: cx

what I do:
calculate the p(topic|doc)
for given terms and p(topic|term)
p(topic|doc) = \sum_term p(topic|term)p(term|doc)
what's my input:
query
DataDir:
    qid_term
    qid_TermTopicProb (also prepare one for Van's TermLevel Method)
what's my output:
    qid_DocTopicProb:
        DocNo\t p1,p2,p3,p4
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

class DocTopicDistributionCalculatorC(cxBaseC):

    def Init(self):
        cxBaseC.Init(self)
        self.QIn = ""
        self.DataDir = ""
        self.CacheDir = ""
        self.TopDocN = 100
        
        
    @staticmethod
    def ShowConf():
        cxBaseC.ShowConf()
        print "cachedir\ntopdocn\ndatadir\nin"
        
    def SetConf(self, ConfIn):
        cxBaseC.SetConf(self, ConfIn)
        self.DataDir = self.conf.GetConf('datadir') + '/'
        self.CacheDir = self.conf.GetConf('cachedir') + '/'
        self.TopDocN = int(self.conf.GetConf('topdocn', self.TopDocN))
        self.QIn = self.conf.GetConf('in')
        
        
    def ReadTermProbVectorForOneQ(self,qid):
        '''
        read term to lTerm
        read TermProb to Vector()
        '''
        lTerm = []
        lTermVector = []
        
        
        TermIn = self.DataDir  + '%d_term' %(qid)
        TermProbIn = self.DataDir + '%d_TermTopicProb' %(qid)
        
        for line in open(TermIn):
            lTerm.append(line.strip())
            
        for line in open(TermProbIn):
            line = line.strip()
            lProb = [float(item) for item in line.split(',')]
            Vector = VectorC(lProb)
            lTermVector.append(Vector)
            
        return lTerm,lTermVector
    
    def CalcDocTopicProb(self,doc,lTerm,lTermVector):
        '''
        p(t|doc) = \sum_i p(t|term_i)p(term_i|doc)
        '''
        lm = LmBaseC(doc)
        
        DocProb = VectorC()
        
        for term in lm.hTermTF.keys():
            if not term in lTerm:
                continue
            ptdoc = lm.GetTFProb(term)
            TermVec = lTermVector[lTerm.Index(term)]
            DocProb = DocProb + TermVec * ptdoc
        return DocProb
    
    def ProcessOneQ(self,qid,query):
        lDoc = ReadPackedIndriRes(self.CacheDir + query, self.TopDocN)
        qid = int(qid)
        lTerm,lTermVector = self.ReadTermProbVectorForOneQ(qid)
        
        out = open("%d_DocTopicProb" %(qid),'w')
        
        for doc in lDoc:
            DocProb = self.CalcDocTopicProb(doc, lTerm, lTermVector)
            print >>out, doc.DocNo + '\t' + DocProb.dumps()
            
        out.close()
        print "query [%d][%s] doc prob get" %(qid,query)
        return

    def Process(self):
        
        for line in open(self.QIn):
            qid,query = line.strip().split('\t')
            self.ProcessOneQ(qid, query)
            
        print "all query doc topic prob calculated"
        
        
        
import sys

if 2 != len(sys.argv):
    DocTopicDistributionCalculatorC.ShowConf()
    sys.exit()
    
Calcer = DocTopicDistributionCalculatorC(sys.argv[1])

Calcer.Process()
    
    
    
    
            