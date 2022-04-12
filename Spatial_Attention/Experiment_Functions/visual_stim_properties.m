function cfgScreen = visual_stim_properties(cfgScreen, windowRect)
% cfgScreen = visual_stim_properties(cfgScreen, windowRect)
% define the destination rectangle in which visStims will be presented
% width and height should be in visual degrees
% windowRect -> output of PsychImaging('OpenWindow',...), is the fullsize of the screen

[xCentre, yCentre] = RectCenter(windowRect);  % get centre coordinates 
cfgScreen.centre = [xCentre, yCentre];
cfgScreen.destVisStimCentre = [0, 0, angle2pix(cfgScreen, cfgScreen.destRectW), angle2pix(cfgScreen, cfgScreen.destRectH)];
cfgScreen.destVisStimCentre = CenterRect(cfgScreen.destVisStimCentre, windowRect);  % for big central stimulus
% cfgScreen.destVisStimCentreSmall = [0, 0, angle2pix(cfgScreen, cfgScreen.destRectSmallW), angle2pix(cfgScreen, cfgScreen.destRectSmallH)];
% cfgScreen.destVisStimCentreSmall = CenterRect(cfgScreen.destVisStimCentreSmall, windowRect);  % for small central stimulus

% move stimuli 3 degrees to right/left and 2 degress below the fixation dot
% (centre point) + use pixel size of central stimulus (in destRectH and W)
cfgScreen.destVisStimR = cfgScreen.destVisStimCentre + angle2pix(cfgScreen, cfgScreen.visStimToR);  
cfgScreen.destVisStimL = cfgScreen.destVisStimCentre - angle2pix(cfgScreen, cfgScreen.visStimToL);  
% cfgScreen.destVisStimSmallR = cfgScreen.destVisStimCentreSmall + angle2pix(cfgScreen, cfgScreen.visStimToR);  
% cfgScreen.destVisStimSmallL = cfgScreen.destVisStimCentreSmall - angle2pix(cfgScreen, cfgScreen.visStimToL);  
% cfgScreen.destVisStimMedR = (cfgScreen.destVisStimBigR + cfgScreen.destVisStimSmallR)./2;
% cfgScreen.destVisStimMedL = (cfgScreen.destVisStimBigL + cfgScreen.destVisStimSmallL)./2;

% % make the destination rectangle 0.5 degree smaller according in two steps
% visStimRectMatR = [cfgScreen.destVisStimBigR; cfgScreen.destVisStimMedR; cfgScreen.destVisStimSmallR; cfgScreen.destVisStimMedR]';  % destination rect size matrix of right stim
% visStimRectMatL = [cfgScreen.destVisStimBigL; cfgScreen.destVisStimMedL; cfgScreen.destVisStimSmallL; cfgScreen.destVisStimMedL]';  % destination rect size matrix of left stim
% for stm = 1:length(cfgExp.stimFrm)
%     cfgScreen.destVisStimR{stm} = repmat(visStimRectMatR, 1, ceil(cfgExp.stimFrm(stm)/size(visStimRectMatR, 2)));
%     cfgScreen.destVisStimL{stm} = repmat(visStimRectMatL, 1, ceil(cfgExp.stimFrm(stm)/size(visStimRectMatL, 2)));  
% end
% 
% % rotate stimulus 20 degress on each frame
% visStimAngMatR = 0:cfgExp.stimRotSpeedFrm:360;  % rotation angle of right stim
% visStimAngMatL = 360:-cfgExp.stimRotSpeedFrm:0;  % rotation angle of left stim
% for stm = 1:length(cfgExp.stimFrm)
%     cfgScreen.stimAngleR{stm} = repmat(visStimAngMatR,1,ceil(cfgExp.stimFrm(stm)/length(visStimAngMatR)));  % every cfgExp.stimSpeedFrm = one complete rotation
%     cfgScreen.stimAngleL{stm} = repmat(visStimAngMatL,1,ceil(cfgExp.stimFrm(stm)/length(visStimAngMatL)));  
% end
 
% calculate the centre of visual stimuli (for dot flash presentation)
cfgScreen.rectLR = [CenterRect(cfgScreen.fixDotRect, cfgScreen.destVisStimL)...
    ; CenterRect(cfgScreen.fixDotRect, cfgScreen.destVisStimR)];  % put both rects in one matrix for use in another function

% destination of cue
rectCue = [0, 0, angle2pix(cfgScreen, cfgScreen.destRectCueSize), angle2pix(cfgScreen, cfgScreen.destRectCueSize)];
cfgScreen.destCue = CenterRect(rectCue, windowRect) + angle2pix(cfgScreen, cfgScreen.cueToB);  % move cue stim to bottom

end

