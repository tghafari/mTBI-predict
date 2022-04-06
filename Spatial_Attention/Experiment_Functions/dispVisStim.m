function cfgOutput = dispVisStim(window, presentingStr, nstim, cfgScreen, cfgExp, cfgOutput, cfgStim, cfgTrigger)
% cfgOutput = dispVisStim(window, presentingStr, nstim, cfgScreen, cfgExp,
% cfgOutput, cfgStim, cfgTrigger)
% draw ans flip visual stimulus with coordinates in cfgScreen
% for the duration specified in cfgExp

if cfgExp.corrResp(nstim)
    cfgOutput.stmOnTmPnt(nstim) = triggerSend(cfgTrigger, cfgExp, cfgTrigger.stimOn);  % send the stim on trigger
    for frm = 1:cfgExp.stimFrm(nstim)
        Screen('DrawTextures', window, [presentingStr.visStimR{nstim}, presentingStr.visStimL{nstim}]...
            , [], [cfgScreen.destVisStimR', cfgScreen.destVisStimL']);
        Screen('FillOval', window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
        Screen('Flip', window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
    end
    cfgOutput.dotOnTmPnt(nstim) = triggerSend(cfgTrigger, cfgExp, cfgTrigger.dotOn);  % send trigger for dot on
    for frm = 1:cfgExp.dotFrm
        Screen('DrawTextures', window, [presentingStr.visStimR{nstim}, presentingStr.visStimL{nstim}]...
            , [],[cfgScreen.destVisStimR', cfgScreen.destVisStimL']);
        Screen('FillOval', window, [cfgScreen.fixDotColor', cfgScreen.fixDotFlashColor']...
            , [cfgScreen.fixDotRect', cfgScreen.rectLR(cfgStim.cueRndIdx(nstim)-2,:)']); %,cfgStim.cueRndIdx(nstim)])']);  % put the red dot according to the cue direction(cueRandIdx-> 3:left, 4:right)
        Screen('Flip', window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
    end
    Screen('FillOval', window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
    Screen('Flip', window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
    cfgOutput.dotOffTmPnt(nstim) = triggerSend(cfgTrigger, cfgExp, cfgTrigger.dotOff);  % trigger dot off
    cfgOutput.stmOffTmPnt(nstim) = triggerSend(cfgTrigger, cfgExp, cfgTrigger.stimOff);  % trigger stim off
    cfgOutput.respStartTime(nstim) = GetSecs; %to get reaction times relative to stimulus offset
else
    cfgOutput.stmOnTmPnt(nstim) = triggerSend(cfgTrigger, cfgExp, cfgTrigger.stimOn);  % trigger stim on
    for frm = 1:cfgExp.stimFrm(nstim)
        Screen('DrawTextures', window, [presentingStr.visStimR{nstim}, presentingStr.visStimL{nstim}]...
            , [], [cfgScreen.destVisStimR', cfgScreen.destVisStimL']);
        Screen('FillOval', window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
        Screen('Flip', window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
    end
    Screen('FillOval', window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
    Screen('Flip', window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
    cfgOutput.stmOffTmPnt(nstim) = triggerSend(cfgTrigger, cfgExp, cfgTrigger.stimOff);  % trigger stim off
    cfgOutput.respStartTime(nstim) = GetSecs; %to get reaction times relative to stimulus offset
end
end

