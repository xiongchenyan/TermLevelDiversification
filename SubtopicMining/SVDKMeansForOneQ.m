function flag = SVDKMeansForOneQ(InName,OutName,k,ReducedDim )
%directly kmeans the cvs data in InName

InData = csvread(InName);
X=spconvert(InData);
[U,S,V] = svd(X);
M=U(:,1:ReducedDim);
[idx,C,sumd,D]=kmeans(M,k);

D = D ./(D* ones(size(D,1),1) * ones(1,size(D,2)));
csvwrite(D,OutName);
flag=  1;
end

