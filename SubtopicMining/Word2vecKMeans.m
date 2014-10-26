function flag = Word2vecKMeans(InName,OutName,k)
%directly kmeans the cvs data in InName

X = csvread(InName);
[idx,C,sumd,D]=kmeans(X,k);
D = D ./(D* ones(size(D,1),1) * ones(1,size(D,2)));
csvwrite(D,OutName);
flag=  1;


