function cfgExp = time2frame(cfgExp, cfgScreen)
% cfgExp = time2frame(cfgExp, cfgScreen)
% inputs what should the durations be from experiment config
% converts time durations to frames

cfgExp.ITIFrm =  round(ms2sec(cfgExp.ITIDur) / cfgScreen.ifi);  % ITI duration in frames
cfgExp.cueFrm =  round(ms2sec(cfgExp.cueDur) / cfgScreen.ifi);  % cue duration in frames
cfgExp.ISIFrm =  round(ms2sec(cfgExp.ISIDur) / cfgScreen.ifi);  % ISI duration in frames
cfgExp.stimFrm = round(ms2sec(cfgExp.stimDur) / cfgScreen.ifi);  % visual stimulus duration in frames
cfgExp.stimSpeedFrm = cfgExp.stimSpeed/round(1/cfgScreen.ifi);  % number of 360-degree rotations per frame
cfgExp.dotFrm =  round(ms2sec(cfgExp.dotDur) / cfgScreen.ifi);  % dot duration in frames
cfgExp.respTimOutFrm =  round(ms2sec(cfgExp.respTimOut) / cfgScreen.ifi);  % response time out duration in frames

end

