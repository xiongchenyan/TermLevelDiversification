'''
Created on Nov 9, 2014 9:59:01 PM
@author: cx

what I do:
for a dir, collect all target eva metrics of all method,
and form a table
what's my input:
a dir of eva files
what's my output:
a file contain the table of method-metrics

'''
import site
site.addsitedir('/bos/usr0/cx/PyCode/TermLevelDiversification')
site.addsitedir('/bos/usr0/cx/PyCode/cxPyLib')
import sys
from cxBase.WalkDirectory import WalkDir
import ntpath

lTarget=['ERR-IR@20','alpha-DCG@20','NRBP','P-IA@20']


def ReadOneMethod(InName):
    lRes = []
    
    lLines = open(InName).readlines()
    head = lLines[0]
    ResStr = lLines[-1]
    
    vHeadCol = head.strip().split(',')
    vTailCol = ResStr.strip().split(',')
    
    for i in range(len(vHeadCol)):
        if vHeadCol[i] in lTarget:
            lRes.append(vTailCol[i])
    return lRes


def Process(InDir,OutName):
    out = open(OutName,'w')
    
    for fName in WalkDir(InDir):
        lRes = ReadOneMethod(fName)
        print >> out, ntpath.basename(fName) + "\t" + " ".join(lRes)
    out.close()
    
    
if 3 != len(sys.argv):
    print "result dir + outputname"
    sys.exit()
    
Process(sys.argv[1],sys.argv[2])
        




