function makeshim
Nch=32;
Nsamples = 0;
frequency = 1e5;
trigger_count = 1000;
filename = 'test_phase_90.mat';

% Make shim vector:
shim=zeros(Nch,3,Nsamples);
if Nsamples>=1
    for a=1:Nsamples
        shim(:,1,a)=0.7;%a/1500; %Amplitude either in V (for high gain) or 0 to 1 for low gain.
        shim(:,2,a)=90; %Phase in degree.
        shim(:,3,a)=1; %Amplifier mode (0: Low power, 1: high power).
    end
else
    shim(:,1)=1;
    shim(:,2)=CP_shim32;
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