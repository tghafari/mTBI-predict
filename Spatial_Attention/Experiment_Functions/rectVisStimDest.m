function cfgScreen = rectVisStimDest(cfgScreen, windowRect)
% cfgScreen = rectVisStimDest(cfgScreen, windowRect)
% define the destination rectangle in which visStims will be presented
% width and height should be in visual degrees
% windowRect -> output of PsychImaging('OpenWindow',...), is the fullsize of the screen

[xCentre, yCentre] = RectCenter(windowRect);  % get centre coordinates 
cfgScreen.centre = [xCentre, yCentre];

cfgScreen.destVisStimCentre = [0, 0, angle2pix(cfgScreen, cfgScreen.destRectW), angle2pix(cfgScreen, cfgScreen.destRectH)];
cfgScreen.destVisStimCentre = CenterRect(cfgScreen.destVisStimCentre, windowRect);  % for a central stimulus

% move stimuli 3 degrees to right/left and 2 degress below the fixation dot
% (centre point) + use pixel size of central stimulus (in destRectH and W)
cfgScreen.destVisStimR = cfgScreen.destVisStimCentre + angle2pix(cfgScreen, cfgScreen.visStimToR);  
cfgScreen.destVisStimL = cfgScreen.destVisStimCentre - angle2pix(cfgScreen, cfgScreen.visStimToL);  

% calculate the centre of visual stimuli (for dot flash presentation)
cfgScreen.rectLR = [CenterRect(cfgScreen.fixDotRect, cfgScreen.destVisStimL)...
    ; CenterRect(cfgScreen.fixDotRect, cfgScreen.destVisStimR)];  % put both rects in one matrix for use in another function

% destination of cue
rectCue = [0, 0, angle2pix(cfgScreen, cfgScreen.destRectCueSize), angle2pix(cfgScreen, cfgScreen.destRectCueSize)];
cfgScreen.destCue = CenterRect(rectCue, windowRect) + angle2pix(cfgScreen, cfgScreen.cueToB);  % move cue stim to bottom

end

