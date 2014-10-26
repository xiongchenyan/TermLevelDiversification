function flag = SubtopicKMeansPipeRun(DataDir)
%pipe line run multiple ways of kmeans of given data in DataDir
%   for each query:
    % cluster word-word cooccurance matrix
    % cluster SVDed w-w cooc matrix
    % cluster word2vec matrix

k = 10;
DimReduce = 300;
for qid=1:200
    fprintf('start clustering [%d]\n',qid);
    RawCoocInName = strcat(DataDir,'/',int2str(qid),'_occur');
    RawKmeansOutName = strcat(RawCoocInName,'_kmeans');
    SVDKmeansOutName = strcat(RawCoocInName,'_svdkmeans');
    WordvecInName = strcat(DataDir,'/',int2str(qid),'_word2vec');
    WordvecOutName =  strcat(WordvecInName,'_kmeans');    
    KMeansForOneQ(RawCoocInName,RawKmeansOutName,k);
    fprintf('kmeans done\n');
    SVDKmeansForOneQ(RawCoocInName,SVDKmeansOutName,k,DimReduce);
    fprintf('svd kmeans done\n');
 %   Word2vecKMeans(WordvecInName,WordvecOutName,k);
 %   fprintf('wordvec kmeans done\n');
end
flag = 1;
return

