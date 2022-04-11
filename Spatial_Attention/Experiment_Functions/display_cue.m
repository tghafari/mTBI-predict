function cfgOutput = display_cue(window, presentingStr, nstim, cfgScreen, cfgExp, cfgTrigger, cfgOutput)
% cfgOutput = display_cue(window, presentingStr, nstim, cfgScreen, cfgExp, cfgTrigger, cfgOutput)
% draw ans flip fixation cross with coordinates in cfgScreen
% for the duration specified in cfgExp

cfgOutput.cueOnTmPnt(nstim) = triggerSend(cfgTrigger, cfgExp, cfgTrigger.cueOn);
for frm = 1:cfgExp.cueFrm
    Screen('DrawTexture', window, presentingStr.cueStim{nstim}, [], cfgScreen.destCue);
    Screen('FillOval', window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
    Screen('Flip', window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
end
cfgOutput.cueOffTmPnt(nstim) = triggerSend(cfgTrigger, cfgExp, cfgTrigger.cueOff);

end

