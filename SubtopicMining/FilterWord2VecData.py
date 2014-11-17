'''
Created on my MAC Nov 16, 2014-8:20:04 PM
What I do:
I filter word2vec data in the dir
What's my input:
Topic term file for each query
word2vec feature, and terms in DataDir
What's my output:
a new word2vec feature and term, filtered so that on terms as topic terms are picked
@author: chenyanxiong
'''



import site
site.addsitedir('/bos/usr0/cx/PyCode/cxPyLib')


from cxBase.base import cxBaseC
from cxBase.Conf import cxConfC

class FilterWord2VecC(cxBaseC):
    def Init(self):
        self.DataDir = ""
        self.TopicTermIn = ""
        self.OutSuf = '_filter'
        
    def SetConf(self, ConfIn):
        cxBaseC.SetConf(self, ConfIn)
        self.DataDir = self.conf.GetConf('datadir')
        self.TopicTermIn = self.conf.GetConf('in')

    @staticmethod
    def ShowConf():
        cxBaseC.ShowConf()
        print "datadir\nin"
        
        
    def LoadTopicTerm(self):
        lQid = []
        llTerm = []
        
        for line in open(self.TopicTermIn):
            qid,query,term,score = line.strip().split('\t')
            if [] == lQid:
                lQid.append(qid)
                llTerm.append([term])
                continue
            if qid != lQid[-1]:
                lQid.append(qid)
                llTerm.append([term])
                continue
            llTerm[-1].append(term)
        return lQid,llTerm
    
    def FilterPerQ(self,qid,lTerm):
        Word2VecName = self.DataDir + '/%s_word2vec' %(qid)
        Word2VecTerm = Word2VecName + '_term'
        
        lWord2VecLine = open(Word2VecName).read().split('\n')
        lWord2VecTerm = open(Word2VecTerm).read().split('\n')
        
        VecOut = open(Word2VecName + self.OutSuf,'w')
        TermOut = open(Word2VecTerm + self.OutSuf,'w')
        
        for i in range(len(lWord2VecLine)):
            if lWord2VecTerm[i] in lTerm:
                print >> VecOut, lWord2VecLine[i]
                print >> TermOut,lWord2VecTerm[i]
                
        VecOut.close()
        TermOut.close()
        
        
        
    def Process(self):
        lQid,llTerm = self.LoadTopicTerm()
        for i in range(len(lQid)):
            self.FilterPerQ(lQid[i], llTerm[i])
            print "[%s] finished" %(lQid[i])
        print 'all finished'
        
        
import sys

if 2 != len(sys.argv):
    FilterWord2VecC.ShowConf()
    sys.exit()
    
Processor = FilterWord2VecC(sys.argv[1])
Processor.Process()

        
        
        
        
        
        
        
                
        
        
    
