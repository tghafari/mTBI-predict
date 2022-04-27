function  cfgTrigger = introduce_triggers
%[trigOff,trigStart,trigVisOn,trigVisOff,trigAud,trigFrqTag,trigTrialInfo] = introduce_triggers
% trigger bits and codes for triggerInit and triggerSend
STI001 = 1;  STI002 = 2;  STI003 = 4;  STI004 = 8; 
STI005 = 16; STI006 = 32; STI007 = 64; STI008 = 128;
STI009 = 256; % STI010 = 512;  STI011 = 1024;

cfgTrigger.off = 0;
cfgTrigger.start = STI001;
cfgTrigger.cueOn = STI002;
cfgTrigger.cueOff = STI003;
cfgTrigger.stimOn = STI004;  % difference between cue off and stim on is the ISI
cfgTrigger.dotOn = STI005;
cfgTrigger.dotOff = STI006;
cfgTrigger.catchOn = STI007;  % for catch trials
cfgTrigger.stimOff = STI008;  % difference between stim off and start is the ITI
cfgTrigger.resp = STI009;  % button press

end
