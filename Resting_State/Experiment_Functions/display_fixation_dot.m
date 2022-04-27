function display_fixation_dot(cfgScreen, cfgExp)
% display_fixation_dot(cfgScreen, cfgExp)
% draw and flip fixation cross with coordinates in cfgScreen
% for the duration specified in cfgExp for resting state

for frm = 1:cfgExp.restFrm
    Screen('FillOval', cfgScreen.window, cfgScreen.fixDotColor, cfgScreen.fixDotRect);
    Screen('Flip', cfgScreen.window, cfgScreen.vbl + (cfgScreen.waitFrm - 0.5) * cfgScreen.ifi);
end

end

