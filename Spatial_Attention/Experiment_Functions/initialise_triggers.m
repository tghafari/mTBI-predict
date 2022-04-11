function cfgTrigger = initialise_triggers(cfgExp, cfgTrigger)
%[cfgTrigger.handle, cfgTrigger.address] = initialise_triggers(cfgExp)
% initiates sending triggers to MEG pc and puts everything in cfgTrigger

cfgTrigger.handle = [];
cfgTrigger.address = [];
if cfgExp.MEGLab == 1
  cfgTrigger.address = hex2dec('BFF8');  % check this port address 
  cfgTrigger.handle = io64;
  cfgTrigger.status = io64(cfgTrigger.handle);
  io64(cfgTrigger.handle, cfgTrigger.address, 0);  % reset trigger
end
  
end
