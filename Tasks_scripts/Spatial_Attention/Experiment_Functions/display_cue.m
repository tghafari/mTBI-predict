function cfgOutput = display_cue(presentingStr, nstim, cfgStim, cfgScreen, cfgExp, cfgTrigger, cfgOutput, cfgEyelink)
% cfgOutput = display_cue(presentingStr, nstim, cfgStim, cfgScreen, cfgExp, cfgTrigger, cfgOutput, cfgEyelink)
% draw ans flip fixation cross with coordinates in cfgScreen
% for the duration specified in cfgExp

cfgOutput.cueOnTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, str2double(cfgTrigger.cuesDir{nstim,1}), cfgEyelink...
    , sprintf('cue onset to %s', cfgTrigger.cuesDir{nstim,2}));

for frm = 1:cfgExp.cueFrm
    Screen('DrawTexture', cfgScreen.window, presentingStr.cueStim{nstim}, [], cfgStim.destCue);
    Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
    Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
end

cfgOutput.cueOffTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.cueOff, cfgEyelink, 'cue offset');

end

