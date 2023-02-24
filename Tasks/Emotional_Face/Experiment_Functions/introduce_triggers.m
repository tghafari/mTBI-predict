function  cfgTrigger = introduce_triggers
% cfgTrigger = introduce_triggers
% trigger bits and codes for triggerInit and triggerSend
% below is the list of stim channels and their corresponding code:
% STI001 = 1;  STI002 = 2;  STI003 = 4;  STI004 = 8; 
% STI005 = 16; STI006 = 32; STI007 = 64; STI008 = 128;
% for mor info check github wiki
% (https://github.com/tghafari/mTBI-predict/wiki/2.1.-MEG-and-Eyetracker-coding-schemes)

% change all on, off, start, end to onset and offset
cfgTrigger.off = 0;
cfgTrigger.trialStart = 1;
cfgTrigger.trialEnd = 2;
cfgTrigger.faceHappy = 101;  % onset of face
cfgTrigger.faceAngry = 102;  % onset of face
cfgTrigger.faceNeutral = 103;  % onset of face
cfgTrigger.faceIDHappy = 110 : 109 + (18 * 2);  % there are 18 female and 18 male faces (36 different identities): 2 frames after onset
cfgTrigger.faceIDAngry = 150 : 149 + (18 * 2);  % 2 frames after face onset
cfgTrigger.faceIDNeutral = 190 : 189 + (18 * 2);  % 2 frames after face onset
cfgTrigger.faceMale = 231;  % 4 frames after onset
cfgTrigger.faceFemale = 232;  % 4 frames after onset
cfgTrigger.faceOff = 104;
cfgTrigger.questionOnset = 105;
cfgTrigger.questionOff = 106;
cfgTrigger.respMale = 254;  % right button press
cfgTrigger.respFemale = 255;  % left button press
cfgTrigger.blkNum = [11, 12, 13];  % corresponding to block number 1, 2, 3
cfgTrigger.blkEnd = 15; 
cfgTrigger.expEnd = 20;
cfgTrigger.abort = 21;


end
