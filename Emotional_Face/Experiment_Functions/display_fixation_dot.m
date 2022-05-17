function display_fixation_dot(cfgScreen, cfgExp, nstim)
% display_fixation_dot(cfgScreen, cfgExp, nstim)  
% draw ans flip fixation cross with coordinates in cfgScreen
% for the duration specified in cfgExp for either ITI or ISI

for frm = 1:cfgExp.ISIFrm(nstim)
    Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
    Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
end

