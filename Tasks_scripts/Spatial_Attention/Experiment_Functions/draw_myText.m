function cfgOutput = draw_myText(cfgScreen, cfgExp, text, cfgTxt, cfgOutput, cfgTrigger, cfgFile, cfgEyelink, cfgStim)
% cfgOutput = draw_myText(cfgScreen, cfgExp, text, cfgTxt, cfgOutput, cfgTrigger, cfgFile, cfgEyelink, cfgStim)
% draws white text on the centre of the Screen and waits for experimenter
% to press "y" to continue

Screen('Flip', cfgScreen.window);
DrawFormattedText(cfgScreen.window, text, 'center', 'center', [cfgScreen.white, cfgScreen.white, cfgScreen.white]);
Screen('Flip', cfgScreen.window);

notWaiting = false;  % only enable the experimenter to continue/ start
while ~notWaiting
    [~, contPresd] = KbStrokeWait(cfgExp.deviceNum);
    if contPresd(cfgExp.yesKey)
        notWaiting = true;
    elseif contPresd(cfgExp.noKey) || contPresd(cfgExp.quitKey)
        Screen('Flip', cfgScreen.window);
        DrawFormattedText(cfgScreen.window, cfgTxt.quitTxt, 'center', 'center', [cfgScreen.white, cfgScreen.white, cfgScreen.white]);
        Screen('Flip', cfgScreen.window);
        [~, abrtPrsd] = KbStrokeWait;
        if abrtPrsd(cfgExp.yesKey)
            cfgOutput.abrtTmPoint = send_trigger(cfgTrigger, cfgExp, cfgTrigger.abort, cfgEyelink...
            , 'Experiment aborted by user');  % send the quit trigger            
            cfgOutput = cleanup(cfgFile, cfgExp, cfgScreen, cfgEyelink, cfgOutput, cfgTrigger, cfgTxt, cfgStim);
            warning('Experiment aborted by user')
            break
        end
    end
    KbQueueFlush;
    WaitSecs(0.5)
end