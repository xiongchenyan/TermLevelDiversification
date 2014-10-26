function flag = SVDKMeansForOneQ(InName,OutName,k,ReducedDim )
%directly kmeans the cvs data in InName

InData = csvread(InName);
X=spconvert(InData);
dim = max(size(X,1),size(X,2));
M = zeros(dim,dim);
M(1:size(X,1),1:size(X,2)) = M(1:size(X,1),1:size(X,2)) + X;
M(1:size(X,2),1:size(X,1)) = M(1:size(X,2),1:size(X,1)) + X';
X=M;
fprintf('read data [%d][%d]\n',size(X,1),size(X,2));
[U,S,V] = svd(X);
M=U(:,1:ReducedDim);
fprintf('reduced to [%d][%d]\n',size(M,1),size(M,2));
[idx,C,sumd,D]=kmeans(M,k,'emptyaction','singleton');

D = D ./(D* ones(size(D,2),1) * ones(1,size(D,2)));
csvwrite(OutName,D);
flag=  1;
end

