function flag = Word2vecKMeans(InName,OutName,k)
%directly kmeans the cvs data in InName

X = csvread(InName);
fprintf('read data [%d][%d]\n',size(X,1),size(X,2));
[idx,C,sumd,D]=kmeans(X,k,'emptyaction','singleton');
D = D ./(D* ones(size(D,1),1) * ones(1,size(D,2)));
csvwrite(D,OutName);
flag=  1;


