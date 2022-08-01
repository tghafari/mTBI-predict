function timepoint = send_trigger(cfgTrigger, cfgExp, code, cfgEyelink, eyelinkMsg)
% timepoint = send_trigger(cfgTrigger, cfgExp, code, cfgEyelink, eyelinkMsg)
% sends trigger during MEG, code should indicate trigger code you want to
% send, eyelinkMsg includes the message you want to send to eyelink as
% trigger

if cfgExp.MEGLab == 1
  io64(cfgTrigger.handle, cfgTrigger.address, code); % send trigger code, e.g., 16 (pin 5)
  WaitSecs(0.005);  % wait 5ms to turn triggers off
  io64(cfgTrigger.handle, cfgTrigger.address, 0); % send trigger code, e.g., 16 (pin 5)
end

if cfgEyelink.on == 1
      Eyelink('Message', eyelinkMsg)
end

timepoint = GetSecs;  % get the time point of interest

end 