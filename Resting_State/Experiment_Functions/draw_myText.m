function draw_myText(cfgScreen, cfgExp, text)
% draw_myText(cfgScreen, cfgExp, text)
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
    end
end
KbQueueFlush;
WaitSecs(0.5)
end