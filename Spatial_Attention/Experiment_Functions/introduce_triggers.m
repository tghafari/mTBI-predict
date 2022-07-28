function  cfgTrigger = introduce_triggers
%[trigOff,trigStart,trigVisOn,trigVisOff,trigAud,trigFrqTag,trigTrialInfo] = introduce_triggers
% trigger bits and codes for triggerInit and triggerSend
% below is the list of stim channels and their corresponding code:
% STI001 = 1;  STI002 = 2;  STI003 = 4;  STI004 = 8; 
% STI005 = 16; STI006 = 32; STI007 = 64; STI008 = 128;
% for mor info check github wiki
% (https://github.com/tghafari/mTBI-predict/wiki/1.1.-MEG-and-Eyetracker-coding-schemes)

cfgTrigger.off = 0;
% cfgTrigger.trialStart = 1; %
% cfgTrigger.trialEnd = 2;
cfgTrigger.cueRight = 101;
cfgTrigger.cueLeft = 102;
cfgTrigger.cueOff = 103;
cfgTrigger.catchTrial = 104;
cfgTrigger.stimOnset = 201;  % difference between cue off and stim on is the ISI
% cfgTrigger.stimOff = 202; % difference between stim off and start is the ITI
cfgTrigger.dotOnRight = 211;
cfgTrigger.dotOnLeft = 212;
% cfgTrigger.dotOff = 213;
cfgTrigger.resp = 255;  %  button press
cfgTrigger.blkNum = [11, 12, 13];  % corresponding to block number 1, 2, 3  (no event for 11)
cfgTrigger.blkEnd = 14;
cfgTrigger.expEnd = 20; 
cfgTrigger.abort = 21;

end
