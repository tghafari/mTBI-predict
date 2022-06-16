function cfgOutput = response_collector(cfgExp, cfgOutput, cfgTrigger, nstim, cfgTxt, cfgScreen, cfgFile, cfgEyelink)
% cfgOutput = response_collector(cfgExp, cfgOutput, cfgTrigger, nstim, cfgTxt, cfgScreen, cfgFile)
% listens for participant's response


noResp = 1;
while noResp
    [presd, firstPrsd] = KbQueueCheck(cfgExp.deviceNum);  % listens for response
    keyCod = find(firstPrsd, 1);  % collects the pressed key code
    
    if presd && ismember(keyCod, cfgExp.responses) % store response variables
        if ismember(keyCod, [cfgExp.NATAKeyM, cfgExp.respKeyM])
            cfgOutput.respTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.respMale, cfgEyelink, 'male button press');  % send the right resp trigger
        elseif ismember(keyCod, [cfgExp.NATAKeyF, cfgExp.respKeyF])
            cfgOutput.respTmPnt(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.respFemale, cfgEyelink, 'female button press');  % send the left resp trigger
        end
        cfgOutput.respTmKbQueue(nstim) = firstPrsd(keyCod);  % exact time of button press - more useful
        cfgOutput.keyName{nstim} = KbName(keyCod);  % which key was pressed
        cfgOutput.RT_KbQueue(nstim) = cfgOutput.respTmKbQueue(nstim) - cfgOutput.respStartTime(nstim);  % calculates RT - using time point in KbQueue
        if cfgExp.quesPres(nstim)
            cfgOutput.RT_trig(nstim) = cfgOutput.respTmPnt(nstim) - cfgOutput.questionOffTmPnt(nstim);  % calculates RT - using triggers
        end
        KbQueueFlush;
        noResp = 0;
        break
    elseif presd && keyCod == cfgExp.quitKey
        Screen('Flip', cfgScreen.window);
        DrawFormattedText(cfgScreen.window, cfgTxt.quitTxt, 'center', 'center', [cfgScreen.white, cfgScreen.white, cfgScreen.white]);
        Screen('Flip', cfgScreen.window);
        [~, abrtPrsd] = KbStrokeWait;
        if abrtPrsd(cfgExp.yesKey)
            cfgOutput.abrtTmPoint = send_trigger(cfgTrigger, cfgExp, cfgTrigger.abort, cfgEyelink, 'Experiment aborted by operator');  % send the quit trigger
            cfgOutput = cleanup(cfgFile, cfgExp, cfgScreen, cfgEyelink, cfgOutput, cfgTrigger);
            warning('Experiment aborted by user')
            break
        end
        KbQueueFlush;
    end
    
    if (GetSecs - cfgOutput.respStartTime(nstim)) > ms2sec(cfgExp.respTimOut)  % stop listening after 500msec
        noResp = 0;
        break
    end
end
end


