function  cfgTrigger = introduce_triggers
% cfgTrigger = introduce_triggers
% trigger bits and codes for triggerInit and triggerSend
% STI001 = 1;  STI002 = 2;  STI003 = 4;  STI004 = 8; 
% STI005 = 16; STI006 = 32; STI007 = 64; STI008 = 128;
% STI009 = 256; STI010 = 512;  STI011 = 1024;

cfgTrigger.off = 0;  % end of resting state
cfgTrigger.restStart = 1;  % start of resting state
cfgTrigger.restEnd = 2;  % end of resting state
cfgTrigger.abort = 21;  % abort 

end
