function test_append
N=1000000;
tic
c=[];
for a = 1:N
c=[c a];
end
toc
size(c)
c1=ones(1,N/2);
c2=ones(1,N/2);

tic
c=[c1 c2];
toc

size(c)