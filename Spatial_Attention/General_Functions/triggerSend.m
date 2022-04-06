function timepoint = triggerSend(cfgTrigger, cfgExp, code)
% timepoint = triggerSend(cfgTrigger, cfgExp, code)
% sends trigger during MEG, code should indicate trigger code you want to
% send

if cfgExp.MEGLab == 1
  io64(cfgTrigger.handle, cfgTrigger.address, code); % send trigger code, e.g., 16 (pin 5)
end

timepoint = GetSecs;  % get the time point of interest

end 