function cfgOutput = display_visual_stim(presentingStr, nstim, cfgScreen, cfgExp, cfgOutput, cfgStim, cfgTrigger)
% cfgOutput = display_visual_stim(presentingStr, nstim, cfgScreen, cfgExp, cfgOutput, cfgStim, cfgTrigger)
% draw ans flip visual stimulus with coordinates in cfgScreen
% for the duration specified in cfgExp

if cfgExp.corrResp(nstim)
    cfgOutput.stmOnTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.stimOn);  % send the stim on trigger
    for frm = 1:cfgExp.stimFrm(nstim)
        Screen('DrawTextures', cfgScreen.window, [presentingStr.visStimR{nstim}{frm}, presentingStr.visStimL{nstim}{frm}]...
            , [], [cfgStim.destVisStimR; cfgStim.destVisStimL]');
        Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
        Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
    end
    cfgOutput.dotOnTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.dotOn);  % send trigger for dot on
    for frm = 1:cfgExp.dotFrm
        Screen('DrawTextures', cfgScreen.window, [presentingStr.visStimR{nstim}{frm}, presentingStr.visStimL{nstim}{frm}]...
            , [],[cfgStim.destVisStimR; cfgStim.destVisStimL]');
        Screen('FillOval', cfgScreen.window, [cfgScreen.fixDotColor', cfgScreen.fixDotFlashColor']...
            , [cfgScreen.fixDotRect', cfgStim.rectLR(cfgStim.cueRndIdx(nstim),:)']);  % put the red dot according to the cue direction(cueRandIdx-> 1:left, 2:right)
        Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
    end
    Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
    Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
    cfgOutput.dotOffTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.dotOff);  % trigger dot off
    cfgOutput.stmOffTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.stimOff);  % trigger stim off
    cfgOutput.respStartTime(nstim) = GetSecs; % to get reaction times relative to stimulus offset
else
    cfgOutput.stmOnTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.stimOn);  % trigger stim on
    for frm = 1:cfgExp.stimFrm(nstim)
        Screen('DrawTextures', cfgScreen.window, [presentingStr.visStimR{nstim}{frm}, presentingStr.visStimL{nstim}{frm}]...
            , [], [cfgStim.destVisStimR; cfgStim.destVisStimL]');
        Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
        Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
    end
    Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
    Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
    cfgOutput.stmOffTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.stimOff);  % trigger stim off
    cfgOutput.respStartTime(nstim) = GetSecs; % to get reaction times relative to stimulus offset
end
end

