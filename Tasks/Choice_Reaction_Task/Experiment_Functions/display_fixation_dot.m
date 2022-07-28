function display_fixation_dot(cfgScreen, cfgExp)
% display_fixation_dot(cfgScreen, cfgExp)  
% draw ans flip fixation cross with coordinates in cfgScreen
% for the duration specified in cfgExp for ISI

for frm = 1:cfgExp.ISIFrm
    Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
    Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
end

end

