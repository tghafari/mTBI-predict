function cfgScreen = fix_dot_properties(cfgScreen)
% cfgScreen = fix_dot_properties(cfgScreen);
% input is screen and window info, outputs characteristics of fixation dot
% Screen('DrawDots'...) will read from this function's output

% Surrounding fixation dot
cfgScreen.fixDotCentreBig = cfgScreen.centre;  % -100 coordinates of fixation dot- normally above center
cfgScreen.fixDotSizeBig = 0.7;  % size of fixation dot in visual degrees
cfgScreen.fixDotRectBig = [cfgScreen.fixDotCentreBig - angle2pix(cfgScreen, cfgScreen.fixDotSizeBig./2)...
    , cfgScreen.fixDotCentreBig + angle2pix(cfgScreen, cfgScreen.fixDotSizeBig./2)];  % rect for fixation dot 
cfgScreen.fixDotColorBig = [1 1 1];  % color of fixation dot in rgb (white)

% Centre fixation dot
cfgScreen.fixDotCentreSmall = cfgScreen.centre;  % -100 coordinates of fixation dot- normally above center
cfgScreen.fixDotSizeSmall = 0.4;  % size of fixation dot in visual degrees
cfgScreen.fixDotRectSmall = [cfgScreen.fixDotCentreSmall - angle2pix(cfgScreen, cfgScreen.fixDotSizeSmall./2)...
    , cfgScreen.fixDotCentreSmall + angle2pix(cfgScreen, cfgScreen.fixDotSizeSmall./2)];  % rect for fixation dot 
cfgScreen.fixDotColorSmall = [0 0 0];  % color of fixation dot in rgb (black)

% Inputs to 'fillOval'
cfgScreen.fixDotRect = [cfgScreen.fixDotRectBig; cfgScreen.fixDotRectSmall]';  % rect for fixation dots 
cfgScreen.fixDotColor = [cfgScreen.fixDotColorBig; cfgScreen.fixDotColorSmall]';  % color of fixation dot in rgb
cfgScreen.fixDotFlashColor = [1 0 0];  % color of fixation dot in rgb (red) when it flashes for participant's response

end

