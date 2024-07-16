function  cfgTrigger = introduce_triggers
% cfgTrigger = introduce_triggers
% trigger bits and codes for triggerInit and triggerSend
% below is the list of stim channels and their corresponding code:
% STI001 = 1;  STI002 = 2;  STI003 = 4;  STI004 = 8; 
% STI005 = 16; STI006 = 32; STI007 = 64; STI008 = 128;
% for mor info check github wiki
% (https://github.com/tghafari/mTBI-predict/wiki/2.1.-MEG-and-Eyetracker-coding-schemes)


cfgTrigger.off = 0;
cfgTrigger.trialStart = 1; 
% cfgTrigger.trialEnd = 2;
cfgTrigger.cueRight = 101;
cfgTrigger.cueLeft = 102;
cfgTrigger.cueOff = 103;
cfgTrigger.catchTrial = 104;
cfgTrigger.respRight = 254;  % right button press
cfgTrigger.respLeft = 255;  % left button press
cfgTrigger.blkNum = [11, 12, 13, 14];  % corresponding to block number 1, 2, 3, 4
cfgTrigger.blkEnd = 15;
cfgTrigger.expEnd = 20;
cfgTrigger.abort = 21;


end
