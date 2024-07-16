function cfgOutput = response_collector(cfgExp, cfgOutput, cfgTrigger, nstim, cfgTxt, cfgScreen, cfgFile, cfgEyelink, cfgCue)
% cfgOutput = response_collector(cfgExp, cfgOutput, cfgTrigger, nstim, cfgTxt, cfgScreen, cfgFile, cfgEyelink, cfgCue)
% listens for participant's response

noResp = 1;
while noResp
    [presd, firstPrsd] = KbQueueCheck(cfgExp.deviceNum);  % listens for response
    keyCod = find(firstPrsd, 1);  % collects the pressed key code
    
    if presd && ismember(keyCod, cfgExp.responses) % store response variables
        if ismember(keyCod, [cfgExp.NATAKeyR, cfgExp.AstonNottKeyR, cfgExp.respKeyR])
            cfgOutput.respTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.respRight, cfgEyelink, 'right button press');  % send the resp trigger
            WaitSecs(0.002);  % wait to make sure the response trigger is reset
        elseif ismember(keyCod, [cfgExp.NATAKeyL, cfgExp.AstonNottKeyL, cfgExp.respKeyL])
            cfgOutput.respTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.respLeft, cfgEyelink, 'left button press');  % send the resp trigger
            WaitSecs(0.002);  % wait to make sure the response trigger is reset
        end
        cfgOutput.respTmKbQueue(nstim) = firstPrsd(keyCod);  % exact time of button press - more useful
        cfgOutput.keyName{nstim} = KbName(keyCod);  % which key was pressed
        cfgOutput.RT_KbQueue(nstim) = cfgOutput.respTmKbQueue(nstim) - cfgOutput.cueOnTmPnt(nstim);  % calculates RT - using time point in KbQueue
        cfgOutput.RT_trig(nstim) = cfgOutput.respTmPnt(nstim) - cfgOutput.cueOnTmPnt(nstim);  % calculates RT - using triggers
        
        KbQueueFlush;
        noResp = 0;
        break
    elseif ~presd
        cfgOutput.keyName{nstim} = 'no resp';
    elseif presd && keyCod == cfgExp.quitKey
        Screen('Flip', cfgScreen.window);
        DrawFormattedText(cfgScreen.window, cfgTxt.quitTxt, 'center', 'center', [cfgScreen.white, cfgScreen.white, cfgScreen.white]);
        Screen('Flip', cfgScreen.window);
        [~, abrtPrsd] = KbStrokeWait;
        if abrtPrsd(cfgExp.yesKey)
            cfgOutput.abrtTmPoint = send_trigger(cfgTrigger, cfgExp, cfgTrigger.abort, cfgEyelink, 'Experiment aborted by operator');  % send the quit trigger
            cfgOutput = cleanup(cfgFile, cfgExp, cfgScreen, cfgEyelink, cfgOutput, cfgTrigger, cfgTxt, cfgCue);
            warning('Experiment aborted by operator')
            break
        end
        KbQueueFlush;
    end
    
    if (GetSecs - cfgOutput.cueOnTmPnt(nstim)) > ms2sec(cfgExp.respTimOut)  % stop listening after 1500msec
        KbQueueFlush;
        noResp = 0;
        break
    end
end
end


