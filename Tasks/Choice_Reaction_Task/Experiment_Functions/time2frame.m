function cfgExp = time2frame(cfgExp, cfgScreen)
% cfgExp = time2frame(cfgExp, cfgScreen)
% inputs what should the durations be from experiment config
% converts time durations to frames

cfgExp.cueFrm =  round(ms2sec(cfgExp.cueDur) / cfgScreen.ifi);  % cue duration in frames
cfgExp.ISIFrm =  round(ms2sec(cfgExp.ISIDur) / cfgScreen.ifi);  % ISI duration in frames
cfgExp.respTimOutFrm =  round(ms2sec(cfgExp.respTimOut) / cfgScreen.ifi);  % response time out duration in frames

end

