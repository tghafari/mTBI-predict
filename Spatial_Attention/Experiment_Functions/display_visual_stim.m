function cfgOutput = display_visual_stim(presentingStr, nstim, cfgScreen, cfgExp, cfgOutput, cfgStim, cfgTrigger, cfgEyelink)
% cfgOutput = display_visual_stim(presentingStr, nstim, cfgScreen, cfgExp, cfgOutput, cfgStim, cfgTrigger, cfgEyelink)
% draw ans flip visual stimulus with coordinates in cfgScreen
% for the duration specified in cfgExp

if cfgExp.corrResp(nstim)
    cfgOutput.stmOnTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.stimOn, cfgEyelink...
    , 'stimulus onset');  
    for frm = 1:cfgExp.stimFrm(nstim)
        Screen('DrawTextures', cfgScreen.window, [presentingStr.visStimR{nstim}{frm}, presentingStr.visStimL{nstim}{frm}]...
            , [], [cfgStim.destVisStimR; cfgStim.destVisStimL]');
        Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
        Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
    end
    cfgOutput.dotOnTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, str2double(cfgTrigger.dotDir{nstim,1}), cfgEyelink...
        , sprintf('dot onset to %s', cfgTrigger.dotDir{nstim,2}));
    for frm = 1:cfgExp.dotFrm
        Screen('DrawTextures', cfgScreen.window, [presentingStr.visStimR{nstim}{frm}, presentingStr.visStimL{nstim}{frm}]...
            , [],[cfgStim.destVisStimR; cfgStim.destVisStimL]');
        Screen('FillOval', cfgScreen.window, [cfgScreen.fixDotColor, cfgScreen.fixDotFlashColor']...
            , [cfgScreen.fixDotRect, cfgStim.rectLR(cfgStim.cueRndIdx(nstim),:)']);  % put the red dot according to the cue direction(cueRandIdx-> 1:left, 2:right)
        Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
    end
%     cfgOutput.dotOffTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.dotOff, cfgEyelink...
%         ,'dot offset');  
    Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
    Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
%     cfgOutput.stmOffTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.stimOff, cfgEyelink...
%         ,'stimulus offset');  % trigger stim off
    cfgOutput.respStartTime(nstim) = GetSecs; % to get reaction times relative to stimulus offset
else  % for catch trials
    cfgOutput.catchOnset(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.catchTrial, cfgEyelink...
        , 'catch trial stimulus onset');
    cfgOutput.stmOnTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.stimOn, cfgEyelink...
    , 'stimulus onset');  
    for frm = 1:cfgExp.stimFrm(nstim)
        Screen('DrawTextures', cfgScreen.window, [presentingStr.visStimR{nstim}{frm}, presentingStr.visStimL{nstim}{frm}]...
            , [], [cfgStim.destVisStimR; cfgStim.destVisStimL]');
        Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
        Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
    end
    Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
    Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
%     cfgOutput.stmOffTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.dotOff, cfgEyelink...
%         ,'stimulus offset');  % trigger stim off
    cfgOutput.respStartTime(nstim) = GetSecs; % to get reaction times relative to stimulus offset
end
end

