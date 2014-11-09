'''
Created on Nov 9, 2014 2:43:19 PM
@author: cx

what I do:
run xquad
what's my input:

what's my output:


'''


import site

site.addsitedir('/bos/usr0/cx/PyCode/TermLevelDiversification')
site.addsitedir('/bos/usr0/cx/PyCode/cxPyLib')
from cxBase.base import cxBaseC
from cxBase.Conf import cxConfC
from Reranking.DiversifiedRerank import DiversifiedRerankC
from Reranking.xQuAdReranker import xQuAdRerankerC
from Reranking.PM2Reranker import PM2RerankerC
import sys

if len(sys.argv) != 2:
    DiversifiedRerankC.ShowConf()
    print "model xquad|pm2"

conf = cxConfC(sys.argv[1])
model = conf.GetConf('model')
if model == 'xquad':
    reranker = xQuAdRerankerC(sys.argv[1])
else:
    reranker = PM2RerankerC(sys.argv[1])
    
reranker.Process()
print "finished"