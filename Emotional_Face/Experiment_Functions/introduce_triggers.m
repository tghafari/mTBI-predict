function  cfgTrigger = introduce_triggers
%[trigOff,trigStart,trigVisOn,trigVisOff,trigAud,trigFrqTag,trigTrialInfo] = introduce_triggers
% trigger bits and codes for triggerInit and triggerSend
STI001 = 1;  STI002 = 2;  STI003 = 4;  STI004 = 8; 
STI005 = 16; STI006 = 32; STI007 = 64; STI008 = 128;
% STI009 = 256; STI010 = 512;  STI011 = 1024;

cfgTrigger.off = 0;
cfgTrigger.start = STI001;
cfgTrigger.fixOn = STI002;
cfgTrigger.fixOff = STI003;
cfgTrigger.stimOn = STI004;  % difference between stim off and stim on is the stimDur
cfgTrigger.stimOff = STI005;  % difference between stim off and next stim on is the ISI
cfgTrigger.questionOn = STI006;  % display question
cfgTrigger.questionOff = STI007; 
cfgTrigger.resp = STI008;  % button press

end
