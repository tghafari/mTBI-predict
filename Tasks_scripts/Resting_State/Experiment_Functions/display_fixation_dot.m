function cfgOutput = display_fixation_dot(cfgScreen, cfgExp, cfgTxt, cfgOutput, cfgFile, cfgEyelink, cfgTrigger)
% cfgOutput = display_fixation_dot(cfgScreen, cfgExp, cfgTxt, cfgOutput, cfgFile, cfgEyelink, cfgTrigger)
% draw and flip fixation cross with coordinates in cfgScreen
% for the duration specified in cfgExp for resting state

% waitForQuit = GetSecs;

noResp = 1;  % only enable the experimenter to continue/ start
while noResp


    for frm = 1:cfgExp.restFrm
        [presd, firstPrsd] = KbQueueCheck(cfgExp.deviceNum);  % listens for response
        keyCod = find(firstPrsd, 1);  % collects the pressed key code
        Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
        Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);

        if presd && keyCod == cfgExp.quitKey
            Screen('Flip', cfgScreen.window);
            DrawFormattedText(cfgScreen.window, cfgTxt.quitTxt, 'center', 'center', [cfgScreen.white, cfgScreen.white, cfgScreen.white]);
            Screen('Flip', cfgScreen.window);
            [~, abrtPrsd] = KbStrokeWait;
            if abrtPrsd(cfgExp.yesKey)
                cfgOutput.abrtTmPoint = send_trigger(cfgTrigger, cfgExp, cfgTrigger.abort, cfgEyelink...
                    , 'experiment aborted by user');  % send the quit trigger
                cfgOutput = cleanup(cfgFile, cfgExp, cfgScreen, cfgEyelink, cfgOutput, cfgTrigger);
                warning('Experiment aborted by user')
                break
            end
            KbQueueFlush;
            noResp = false;
            WaitSecs(0.5)
        end
        noResp = false;
    end
end

end
