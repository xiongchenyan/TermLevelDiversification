function flag = SubtopicKMeansPipeRun(DataDir)
%pipe line run multiple ways of kmeans of given data in DataDir
%   for each query:
    % cluster word-word cooccurance matrix
    % cluster SVDed w-w cooc matrix
    % cluster word2vec matrix
    
for qid=1:200
    RawCoocInName = strcat(DataDir,'/',int2str(qid),'_occur');
    RawKmeansOutName = strcat(RawCoocInName,'_kmeans');
    SVDKmeansOutName = strcat(RawCoocInName,'_svdkmeans');

end

