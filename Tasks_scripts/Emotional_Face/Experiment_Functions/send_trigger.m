function timepoint = send_trigger(cfgTrigger, cfgExp, code, cfgEyelink, eyelinkMsg)
% timepoint = send_trigger(cfgTrigger, cfgExp, code, cfgEyelink, eyelinkMsg)
% sends trigger during MEG, code should indicate trigger code you want to
% send, eyelinkMsg includes the message you want to send to eyelink as
% trigger

if cfgExp.MEGLab == 1
  io64(cfgTrigger.handle, cfgTrigger.address, code); % send trigger code, e.g., 16 (pin 5)
  WaitSecs(cfgExp.trgRstTm);  % wait 5ms to turn triggers off
  io64(cfgTrigger.handle, cfgTrigger.address, 0); % reset trigger port
  WaitSecs(cfgExp.trgSftTm);  % wait 3ms to make sure trigger is reset before moving on
end

if cfgEyelink.on == 1
      Eyelink('Message', eyelinkMsg)
end

timepoint = GetSecs;  % get the time point of interest

end 