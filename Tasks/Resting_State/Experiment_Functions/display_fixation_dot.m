function cfgOutput = display_fixation_dot(cfgScreen, cfgExp, cfgTxt, cfgOutput, cfgFile, cfgEyelink, cfgTrigger)
% cfgOutput = display_fixation_dot(cfgScreen, cfgExp, cfgTxt, cfgOutput, cfgFile, cfgEyelink, cfgTrigger)
% draw and flip fixation cross with coordinates in cfgScreen
% for the duration specified in cfgExp for resting state

for frm = 1:cfgExp.restFrm
    Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
    Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
end

notDisplaying = false;  % only enable the experimenter to continue/ start
while ~notDisplaying
    [presd, firstPrsd] = KbQueueCheck(cfgExp.deviceNum);  % listens for response
    keyCod = find(firstPrsd, 1);  % collects the pressed key code
if presd && keyCod == cfgExp.quitKey
        Screen('Flip', cfgScreen.window);
        DrawFormattedText(cfgScreen.window, cfgTxt.quitTxt, 'center', 'center', [cfgScreen.white, cfgScreen.white, cfgScreen.white]);
        Screen('Flip', cfgScreen.window);
        [~, abrtPrsd] = KbStrokeWait;
        if abrtPrsd(cfgExp.yesKey)
            cfgOutput.abrtTmPoint(nstim) = send_trigger(cfgTrigger, cfgExp, cfgTrigger.off);  % send the quit trigger
            cfgOutput = cleanup(cfgFile, cfgExp, cfgScreen, cfgEyelink, cfgOutput, cfgTrigger);
            warning('Experiment aborted by user')
            break
        end
        KbQueueFlush;
        WaitSecs(0.5)
end

end

