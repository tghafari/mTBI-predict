function cfgExp = time2frame(cfgExp, cfgScreen)
% cfgExp = time2frame(cfgExp, cfgScreen)
% inputs what should the durations be from experiment config
% converts time durations to frames

cfgExp.restFrm =  round(ms2sec(cfgExp.restDur) / cfgScreen.ifi);  % resting state duration in frames

end

