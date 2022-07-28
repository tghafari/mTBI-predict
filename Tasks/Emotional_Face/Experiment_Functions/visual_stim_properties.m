function cfgStim = visual_stim_properties(cfgScreen, cfgStim)
% cfgStim = visual_stim_properties(cfgScreen, cfgStim)
% define the destination rectangle in which visStims will be presented
% width and height should be in visual degrees

cfgStim.destVisStimCentre = [0, 0, angle2pix(cfgScreen, cfgStim.destRectW), angle2pix(cfgScreen, cfgStim.destRectH)];
cfgStim.destVisStimCentre = CenterRect(cfgStim.destVisStimCentre, cfgScreen.windowRect);  % for big central stimulus

end

