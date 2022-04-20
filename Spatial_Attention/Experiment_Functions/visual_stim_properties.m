function cfgStim = visual_stim_properties(cfgScreen, cfgStim, cfgExp)
% cfgScreen = visual_stim_properties(cfgScreen, cfgStim, cfgExp)
% define the destination rectangle in which visStims will be presented
% width and height should be in visual degrees

cfgStim.destVisStimCentre = [0, 0, angle2pix(cfgScreen, cfgStim.destRectW), angle2pix(cfgScreen, cfgStim.destRectH)];
cfgStim.destVisStimCentre = CenterRect(cfgStim.destVisStimCentre, cfgScreen.windowRect);  % for big central stimulus

cfgStim.destVisStimR = cfgStim.destVisStimCentre + angle2pix(cfgScreen, cfgStim.visStimToR);  
cfgStim.destVisStimL = cfgStim.destVisStimCentre - angle2pix(cfgScreen, cfgStim.visStimToL);  

cfgStim.visStimMat = [cfgStim.visStim; flip(cfgStim.visStim)];  % matrix of moving gratings
% create enough visual stimuli for each trial
for stm = 1:length(cfgExp.stimFrm)
    cfgStim.visStimR{stm} = repmat(cfgStim.visStimMat, ceil(cfgExp.stimFrm(stm)/length(cfgStim.visStim)/2), 1);  % every cfgExp.stimSpeedFrm = one complete rotation
    cfgStim.visStimL{stm} = repmat(cfgStim.visStimMat, ceil(cfgExp.stimFrm(stm)/length(cfgStim.visStim)/2), 1);  
end

% calculate the centre of visual stimuli (for dot flash presentation)
cfgStim.rectLR = [CenterRect(cfgScreen.fixDotRect, cfgStim.destVisStimL)...
    ; CenterRect(cfgScreen.fixDotRect, cfgStim.destVisStimR)];  % put both rects in one matrix for use in another function

% destination of cue
rectCue = [0, 0, angle2pix(cfgScreen, cfgStim.destRectCueSize), angle2pix(cfgScreen, cfgStim.destRectCueSize)];
cfgStim.destCue = CenterRect(rectCue, cfgScreen.windowRect) + angle2pix(cfgScreen, cfgStim.cueToB);  % move cue stim to bottom

end

