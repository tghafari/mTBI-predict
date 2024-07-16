function cfgExp = time2frame(cfgExp, cfgScreen)
% cfgExp = time2frame(cfgExp, cfgScreen)
% inputs what should the durations be from experiment config
% converts time durations to frames

cfgExp.ISIFrm =  round(ms2sec(cfgExp.ISIDur) / cfgScreen.ifi);  % ISI duration in frames (fixation dot duration)
cfgExp.stimFrm = round(ms2sec(cfgExp.stimDur) / cfgScreen.ifi);  % visual stimulus duration in frames
cfgExp.respTimOutFrm = round(ms2sec(cfgExp.respTimOut) / cfgScreen.ifi);  % response time out duration in frames
cfgExp.quesFrm = round(ms2sec(cfgExp.quesDur) / cfgScreen.ifi);  % question display duration in frames
end

