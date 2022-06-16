function cfgOutput = display_visual_stim(presentingStr, nstim, cfgScreen, cfgExp, cfgOutput, cfgStim, cfgTrigger, cfgEyelink)
% cfgOutput = display_visual_stim(presentingStr, nstim, cfgScreen, cfgExp, cfgOutput, cfgStim, cfgTrigger, cfgEyelink)
% draw ans flip visual stimulus with coordinates in cfgScreen
% for the duration specified in cfgExp

cfgOutput.faceOnTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.faceTrigAll{nstim, 2}, cfgEyelink...
    , sprintf('%s face onset', cfgTrigger.faceTrigAll{nstim, 1}));  % send emotion trigger
for frm = 1:cfgExp.stimFrm(nstim)
    if frm == 2
    cfgOutput.faceIDTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.faceTrigAll{nstim, 4}, cfgEyelink...
    , sprintf('face id = %d', cfgTrigger.faceTrigAll{nstim, 4}));  % send ID trigger
    elseif frm == 4
        cfgOutput.faceSexTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.faceTrigAll{nstim, 6}, cfgEyelink...
    , sprintf('%s face', cfgTrigger.faceTrigAll{nstim, 5}));  % send sex trigger
    end
    Screen('DrawTexture', cfgScreen.window, presentingStr.visStim{nstim}...
        , [], cfgStim.destVisStimCentre);
    Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
    Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
end
cfgOutput.faceOffTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.faceOff, cfgEyelink, 'stimulus offset');
Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);

end

