function dispFixDot(window, cfgScreen, cfgExp, nstim, ITI)
% dispFixDot(window, cfgScreen, cfgExp, ITI)  % ITI = 0>ISI, ITI = 1>ITI
% draw ans flip fixation cross with coordinates in cfgScreen
% for the duration specified in cfgExp for either ITI or ISI

if ITI
    for frm = 1:cfgExp.ITIFrm(nstim)
        Screen('FillOval', window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
        Screen('Flip', window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
    end
else
    for frm = 1:cfgExp.ISIFrm
        Screen('FillOval', window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
        Screen('Flip', window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
    end
end

