'''
Created on my MAC Nov 16, 2014-8:17:37 PM
What I do:
I run DSPApproxC
What's my input:

What's my output:

@author: chenyanxiong
'''



import site
site.addsitedir('/bos/usr0/cx/PyCode/cxPyLib')
site.addsitedir('/bos/usr0/cx/PyCode/GoogleAPI')

from DSPApprox import DSPApproxC
from DSPApproxWord2vec import DSPApproxWord2VecC
from cxBase.Conf import cxConfC
import sys

if 2 != len(sys.argv):
    DSPApproxC.ShowConf()
    sys.exit()

conf = cxConfC(sys.argv[1])
model  = conf.GetConf('model')
if model == 'dsp':
    Approx = DSPApproxC(sys.argv[1])
else:
    Approx = DSPApproxWord2VecC(sys.argv[1])
Approx.Process()