function cfgCue = cue_properties(cfgScreen, cfgCue)
% cfgCue = visual_stim_properties(cfgScreen, cfgCue)
% define the destination rectangle in which visStims will be presented
% width and height should be in visual degrees

% destination of cue
rectCue = [0, 0, angle2pix(cfgScreen, cfgCue.destRectCueSize), angle2pix(cfgScreen, cfgCue.destRectCueSize)];
cfgCue.destCue = CenterRect(rectCue, cfgScreen.windowRect) + angle2pix(cfgScreen, cfgCue.cueToB);  % move cue stim to bottom

end

