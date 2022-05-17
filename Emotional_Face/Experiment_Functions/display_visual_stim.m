function cfgOutput = display_visual_stim(presentingStr, nstim, cfgScreen, cfgExp, cfgOutput, cfgStim, cfgTrigger)
% cfgOutput = display_visual_stim(presentingStr, nstim, cfgScreen, cfgExp, cfgOutput, cfgStim, cfgTrigger)
% draw ans flip visual stimulus with coordinates in cfgScreen
% for the duration specified in cfgExp

cfgOutput.stmOnTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.stimOn);  % trigger stim on
for frm = 1:cfgExp.stimFrm(nstim)
    Screen('DrawTexture', cfgScreen.window, presentingStr.visStim{nstim}...
        , [], cfgStim.destVisStimCentre);
    Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
    Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
end
cfgOutput.stmOffTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.stimOff);  % trigger stim off
Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);

end

