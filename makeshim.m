function makeshim
Nch=32;
Nsamples = 60000;
frequency = 1e5;
trigger_count = 1000;
filename = '.\shims\system_test\TestMode60k.mat';

% Make shim vector:
if Nsamples>0
    shim=zeros(Nch,3,Nsamples);
else
    shim=zeros(Nch,3);
end
if Nsamples>=1
    for a=1:Nsamples
        shim(:,1,a)=abs(0.7*sin(a/100*pi)); %Amplitude either in V (for high gain) or 0 to 1 for low gain.
        shim(:,2,a)=a/10; %Phase in degree.
        if shim(:,1,a)>0.35
            shim(:,3,a)=1; %Amplifier mode (0: Low power, 1: high power).
        else
            shim(:,3,a)=0;
        end
    end
else
    shim(:,1)=1;
    shim(:,2)=CP_shim32*2;
    shim(:,3)=1;
end

% Set gain. (Use 'high', 'low', or integer between -31 and 22)
gain='low';

% Set Oscbit (0 or 1)
OSCbit=1;

% Set trigger. Frequency in Hz and number of triggers. Set to [] for
% feedthrough.
trigger = [frequency,trigger_count];

save(filename,'shim','gain')%,'OSCbit','trigger')

function out=CP_shim32
phase=[];
for a=1:11
    if mod(a,2)==1
        phase = [phase, 180/11*a];
    else
        phase = [phase, 180/11*a, 180/11*a];
    end
end

out = [phase, (phase +180)];