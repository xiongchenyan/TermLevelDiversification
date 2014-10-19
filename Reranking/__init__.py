'''
for given subtopics, rerank documents
input:
    for each q:
        p(term|topic) for its terms
output:
    reranked documents
    
module:
    1, from p(t|topic) -> p(t|doc)
    2, rerank:
        2a, xQuAd
        2b, PM-2
        2c, R-ListMLE (to be done, might in Matlab)
'''