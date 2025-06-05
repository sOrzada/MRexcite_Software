function makeshim
Nch=32;

shim=zeros(Nch,3,10);

shim(:,1,:)=1;
shim(:,2,:)=90;

gain='high';

OSCbit=1;

trigger = [1e6,10];

save('Cp_plus.mat')