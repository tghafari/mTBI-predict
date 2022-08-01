function cfgOutput = display_fixation_dot(cfgScreen, cfgExp, nstim, ITI, cfgOutput)
% cfgOutput = display_fixation_dot(cfgScreen, cfgExp, nstim, ITI, cfgOutput)
% ITI = 0>ISI, ITI = 1>ITI
% draw ans flip fixation cross with coordinates in cfgScreen
% for the duration specified in cfgExp for either ITI or ISI

if ITI
    for frm = 1:cfgExp.ITIFrm(nstim)
        Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
        Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
    end
else
    for frm = 1:cfgExp.ISIFrm
        Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
        Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
    end
end

