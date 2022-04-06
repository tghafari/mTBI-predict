function cfgScreen = fixDotChar(windowRect, cfgScreen)
% cfgScreen = fixDotCoord(windowRect,cfgScreen);
% input is screen and window info, outputs characteristics of fixation dot
% Screen('DrawDots'...) will read from this function's output

[xCentre, yCentre] = RectCenter(windowRect);  % get center coordinates
cfgScreen.fixDotCentre = [xCentre, yCentre];  % -100 coordinates of fixation dot- normally above center
cfgScreen.fixDotSize = 0.2;  % size of fixation dot in visual degrees
cfgScreen.fixDotRect = [cfgScreen.fixDotCentre - angle2pix(cfgScreen, cfgScreen.fixDotSize./2)...
    , cfgScreen.fixDotCentre + angle2pix(cfgScreen, cfgScreen.fixDotSize./2)];  % rect for fixation dot 
cfgScreen.fixDotColor = [1 1 1];  % color of fixation dot in rgb (white)
cfgScreen.fixDotFlashColor = [1 0 0];  % color of fixation dot in rgb (red) when it flashes for participant's response

end

