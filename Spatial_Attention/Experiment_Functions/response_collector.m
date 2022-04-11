function cfgOutput = response_collector(cfgExp, cfgOutput, cfgTrigger, nstim, window, cfgTxt, cfgScreen)
% cfgOutput = response_collector(cfgExp, cfgOutput, cfgTrigger, nstim, window, cfgTxt, cfgScreen)
% listens for participant's response

noResp = 1;
while noResp
    [presd, firstPrsd] = KbQueueCheck(cfgExp.deviceNum);  % listens for response
    keyCod = find(firstPrsd,1);  % collects the pressed key code
    
    if presd && (keyCod == cfgExp.NATAKey || keyCod == cfgExp.respKey)  % store response variables
        cfgOutput.respTmPnt(nstim) = triggerSend(cfgTrigger, cfgExp, cfgTrigger.resp);  % send the resp trigger
        cfgOutput.keyName{nstim} = KbName(keyCod);  % which key was pressed
        cfgOutput.RT_KbQueue(nstim) = firstPrsd(keyCod) - cfgOutput.respStartTime(nstim);  % calculates RT - using time point in KbQueue
        if cfgExp.corrResp(nstim)
        cfgOutput.RT_trig(nstim) = cfgOutput.respTmPnt(nstim) - cfgOutput.dotOnTmPnt(nstim);  % calculates RT - using triggers
        end
        KbQueueFlush;
        noResp = 0;
    elseif presd && keyCod == cfgExp.quitKey
        Screen('Flip', window);
        DrawFormattedText(window, cfgTxt.quitTxt, 'center', 'center', [cfgScreen.white, cfgScreen.white, cfgScreen.white]);
        Screen('Flip', window);
        [~, abrtPrsd] = KbStrokeWait;
        if abrtPrsd(cfgExp.yesKey)
            cfgOutput.abrtTmPoint(nstim) = triggerSend(cfgTrigger, cfgExp, cfgTrigger.off);  % send the quit trigger
            sca
            warning('Experiment aborted by user')
            return
        end
        KbQueueFlush;
    end
    
    if (GetSecs - cfgOutput.respStartTime(nstim)) > ms2sec(cfgExp.respTimOut)  % stop listening after 500msec
        noResp = 0;
    end
end
end


