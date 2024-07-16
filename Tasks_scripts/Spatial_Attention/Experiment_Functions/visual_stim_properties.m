function cfgStim = visual_stim_properties(cfgScreen, cfgStim)
% cfgScreen = visual_stim_properties(cfgScreen, cfgStim)
% define the destination rectangle in which visStims will be presented
% width and height should be in visual degrees

% find the location of visual stim
cfgStim.destVisStimCentre = [0, 0, angle2pix(cfgScreen, cfgStim.destRectW), angle2pix(cfgScreen, cfgStim.destRectH)];
cfgStim.destVisStimCentre = CenterRect(cfgStim.destVisStimCentre, cfgScreen.windowRect);  % for big central stimulus

cfgStim.destVisStimR = cfgStim.destVisStimCentre + angle2pix(cfgScreen, cfgStim.visStimToR);  
cfgStim.destVisStimL = cfgStim.destVisStimCentre - angle2pix(cfgScreen, cfgStim.visStimToL);  

% calculate the centre of visual stimuli (for dot flash presentation)
cfgStim.rectRL = [CenterRect(cfgScreen.fixDotRect(:,2)', cfgStim.destVisStimR)...
    ; CenterRect(cfgScreen.fixDotRect(:,2)', cfgStim.destVisStimL)];  % put both rects in one matrix for use in another function

% destination of cue
rectCue = [0, 0, angle2pix(cfgScreen, cfgStim.destRectCueSize), angle2pix(cfgScreen, cfgStim.destRectCueSize)];
cfgStim.destCue = CenterRect(rectCue, cfgScreen.windowRect) + angle2pix(cfgScreen, cfgStim.cueToB);  % move cue stim to bottom

end

