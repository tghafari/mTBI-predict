function showInstructions(cfgScreen, cfgTxt, cfgExp, presentingStr, cfgCue)

Screen('Flip', cfgScreen.window);
DrawFormattedText(cfgScreen.window, cfgTxt.instrTxt{1}, 'center', 'center', [cfgScreen.white, cfgScreen.white, cfgScreen.white]);
Screen('Flip', cfgScreen.window);

notWaiting = false;  % only enable the experimenter to continue/ start
while ~notWaiting
    [~, contPresd] = KbStrokeWait(cfgExp.deviceNum);
    if contPresd(cfgExp.yesKey)
        notWaiting = true;
    end
    KbQueueFlush;
    WaitSecs(0.5)
end

DrawFormattedText(cfgScreen.window, cfgTxt.instrTxt{2}, 'center', 'center', [cfgScreen.white, cfgScreen.white, cfgScreen.white]);
Screen('Flip', cfgScreen.window);

notWaiting = false;  % only enable the experimenter to continue/ start
while ~notWaiting
    [~, contPresd] = KbStrokeWait(cfgExp.deviceNum);
    if contPresd(cfgExp.yesKey)
        notWaiting = true;
    end
    KbQueueFlush;
    WaitSecs(0.5)
end

DrawFormattedText(cfgScreen.window, cfgTxt.instrTxt{3}, 'center', 'center', [cfgScreen.white, cfgScreen.white, cfgScreen.white]);
Screen('Flip', cfgScreen.window);

notWaiting = false;  % only enable the experimenter to continue/ start
while ~notWaiting
    [~, contPresd] = KbStrokeWait(cfgExp.deviceNum);
    if contPresd(cfgExp.yesKey)
        notWaiting = true;
    end
    KbQueueFlush;
    WaitSecs(0.5)
end

    Screen('DrawTexture', cfgScreen.window, presentingStr.cueStim{2}, [], cfgCue.destCue);
    Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
    Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);

notWaiting = false;  % only enable the experimenter to continue/ start
while ~notWaiting
    [~, contPresd] = KbStrokeWait(cfgExp.deviceNum);
    if contPresd(cfgExp.yesKey)
        notWaiting = true;
    end
    KbQueueFlush;
    WaitSecs(0.5)
end
